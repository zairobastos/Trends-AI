import argparse
import hashlib
import json
import platform
from datetime import datetime, timezone
from itertools import islice
from pathlib import Path


CAMPOS = ("resumo", "proximo_passo", "informacoes_ausentes")
MAX_ITERACOES = 3  # Inclui a avaliação da resposta inicial.
SOLICITACAO = "Não consigo acessar o sistema interno. Aparece uma mensagem de erro."
INICIAL = {"resumo": "Relato de falha no acesso ao sistema interno."}
COMPLETA = {
    **INICIAL,
    "proximo_passo": "Informe qual sistema e a mensagem de erro exibida.",
    "informacoes_ausentes": "Nome do sistema e texto da mensagem de erro.",
}


def avaliar(resposta):
    return {campo: bool(str(resposta.get(campo, "")).strip()) for campo in CAMPOS}


def refinar(resposta, faltantes, sem_melhora=False):
    """Dublê: usa o diagnóstico para preencher somente os campos ausentes."""
    nova = dict(resposta)
    if not sem_melhora:
        nova.update({campo: COMPLETA[campo] for campo in faltantes})
    return nova


def registro(iteracao, resposta, criterios, decisao, motivo):
    faltantes = [campo for campo, ok in criterios.items() if not ok]
    return {
        "iteracao": iteracao,
        "resposta": dict(resposta),
        "criterios": criterios,
        "problemas": faltantes,
        "orientacao": "Preencher: " + ", ".join(faltantes) if faltantes else "Nenhuma.",
        "decisao": decisao,
        "motivo": motivo,
        "aprovado": decisao == "parar" and motivo == "criterios_satisfeitos",
    }


def ciclo_sem_parada():
    """Defeito real: não decide parar nem quando todos os critérios passam."""
    resposta, iteracao = dict(INICIAL), 0
    while True:
        iteracao += 1
        criterios = avaliar(resposta)
        yield registro(iteracao, resposta, criterios, "continuar", "sem_regra_de_parada")
        faltantes = [campo for campo, ok in criterios.items() if not ok]
        resposta = refinar(resposta, faltantes)


def ciclo_corrigido(sem_melhora=False, inicial=None, limite=MAX_ITERACOES):
    if limite < 1:
        raise ValueError("O limite deve ser pelo menos 1.")
    resposta = dict(INICIAL if inicial is None else inicial)
    for iteracao in range(1, limite + 1):
        criterios = avaliar(resposta)
        # Avaliar a satisfação antes do limite evita rejeitar a última versão válida.
        if all(criterios.values()):
            yield registro(iteracao, resposta, criterios, "parar", "criterios_satisfeitos")
            return
        if iteracao == limite:
            yield registro(iteracao, resposta, criterios, "parar", "limite_seguranca")
            return
        yield registro(iteracao, resposta, criterios, "continuar", "criterios_pendentes")
        faltantes = [campo for campo, ok in criterios.items() if not ok]
        resposta = refinar(resposta, faltantes, sem_melhora)


def executar(cenario):
    if cenario == "antes":
        # A bancada observa só seis passos; não é uma parada implementada no agente.
        eventos = list(islice(ciclo_sem_parada(), 6))
        return eventos + [{"bancada": "observacao_encerrada_apos_6", "agente_parou": False}]
    return list(ciclo_corrigido(sem_melhora=cenario == "limite",
                               inicial=COMPLETA if cenario == "pronta" else None))


def verificar():
    antes, criterio, limite = (executar(c) for c in ("antes", "criterio", "limite"))
    checagens = {
        "defeito_persiste_mesmo_apos_criterios": all(antes[1]["criterios"].values())
            and antes[1]["decisao"] == "continuar" and not antes[-1]["agente_parou"],
        "criterio_para_na_iteracao_2": len(criterio) == 2 and criterio[-1]["aprovado"],
        "limite_para_sem_aprovar": len(limite) == 3 and not limite[-1]["aprovado"]
            and limite[-1]["motivo"] == "limite_seguranca",
        "resposta_pronta_para_na_primeira": len(executar("pronta")) == 1,
        "ultima_iteracao_valida_e_aprovada": list(ciclo_corrigido(limite=2))[-1]["aprovado"],
        "limite_1_nao_inventa_aprovacao": not list(ciclo_corrigido(limite=1))[-1]["aprovado"],
    }
    print(json.dumps({"verificacao": checagens}, ensure_ascii=False))
    if not all(checagens.values()):
        raise SystemExit("VERIFICACAO_FALHOU")
    print("VERIFICACAO_OK")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cenario", choices=("antes", "criterio", "limite", "pronta"),
                        default="criterio")
    parser.add_argument("--saida", type=Path,
                        help="Arquivo .json com metadados e uma lista de registros.")
    parser.add_argument("--verificar", action="store_true")
    args = parser.parse_args()
    if args.verificar:
        verificar()
        return
    metadados = {
        "data_utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
        "origem": "duble_deterministico_v1", "modelo": "nao_utilizado",
        "versao_script": "1.1", "cenario": args.cenario, "max_iteracoes": MAX_ITERACOES,
        "sha256_script": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "solicitacao_ficticia": SOLICITACAO,
    }
    conteudo = {"metadados": metadados, "registros": executar(args.cenario)}
    texto = json.dumps(conteudo, ensure_ascii=False, indent=2) + "\n"
    if args.saida:
        args.saida.parent.mkdir(parents=True, exist_ok=True)
        args.saida.write_text(texto, encoding="utf-8")
    print(texto, end="")


if __name__ == "__main__":
    main()
