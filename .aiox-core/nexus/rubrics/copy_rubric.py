"""Copy quality rubric for NEXUS review agents.

Evaluates ad copy quality across 4 dimensions:
hook, cta, length_fit, and persuasion.

Threshold for approval: min_copy_score = 7 (NexusConfig default)
"""

COPY_RUBRIC = {
    "dimension": "copy",
    "description": (
        "Avalia a qualidade do roteiro/copy do anuncio para video publicitario no Meta Ads. "
        "Foco em capacidade de atrair atencao, comunicar valor e gerar acao."
    ),
    "criteria": [
        {
            "name": "hook",
            "weight": 0.3,
            "description": "Qualidade do gancho nos primeiros 3 segundos para prender atencao.",
            "levels": {
                10: "Hook excepcional: cria tensao imediata, surpresa ou promessa irresistivel. Impossivel ignorar.",
                8: "Hook forte: pergunta ou afirmacao relevante que gera curiosidade clara.",
                6: "Hook adequado: abre com beneficio ou problema reconhecivel, mas sem impacto forte.",
                4: "Hook fraco: inicio generico ou apresentacao de produto sem contexto emocional.",
                2: "Sem hook: comeca com branding, saudacao ou contexto irrelevante para o publico.",
            },
        },
        {
            "name": "cta",
            "weight": 0.25,
            "description": "Clareza e forca do call-to-action para gerar clique ou conversao.",
            "levels": {
                10: "CTA especifico, urgente e alinhado com a oferta. Ex: 'Garanta sua vaga antes que acabe — link na bio'.",
                8: "CTA claro com direcao especifica. Ex: 'Clique no link abaixo para saber mais'.",
                6: "CTA presente mas generico. Ex: 'Acesse nosso site'.",
                4: "CTA vago ou desalinhado com a proposta do video.",
                2: "Sem CTA ou instrucao de proxima acao.",
            },
        },
        {
            "name": "length_fit",
            "weight": 0.2,
            "description": "Adequacao do tamanho do roteiro ao formato de video curto (Reels/Stories).",
            "levels": {
                10: "Roteiro compacto e denso: cada palavra tem proposito. Ideal para 30-60 segundos.",
                8: "Ligeiramente longo mas sem partes dispensaveis. Boa densidade de valor.",
                6: "Algumas repeticoes ou enchimento que podem ser cortados sem perder valor.",
                4: "Texto visivelmente longo para o formato. Ritmo prejudicado.",
                2: "Roteiro excessivo (>80 palavras para Stories) ou fragmentado demais para entender.",
            },
        },
        {
            "name": "persuasion",
            "weight": 0.25,
            "description": "Forca persuasiva: uso de gatilhos mentais, prova social e diferenciacao.",
            "levels": {
                10: "Usa 2+ gatilhos (escassez, prova social, autoridade) de forma natural e integrada ao contexto.",
                8: "Um gatilho forte bem executado ou dois moderados que elevam a credibilidade.",
                6: "Algum elemento persuasivo presente mas superficial (numeros genericos, promessa sem contexto).",
                4: "Tentativa de persuasao mas sem especificidade ou credibilidade.",
                2: "Apenas descricao do produto sem argumentacao persuasiva.",
            },
        },
    ],
    "few_shot_examples": [
        {
            "input": (
                "Voce sabia que 9 em cada 10 empreendedores perdem dinheiro por nao conhecer essa estrategia? "
                "Nos ultimos 3 anos, ajudamos mais de 2.400 alunos a sair do vermelho usando o Metodo R3. "
                "Hoje, a inscricao com desconto fecha a meia-noite. Clique no link abaixo e garanta sua vaga."
            ),
            "expected_score": 8,
            "expected_total": 8,
            "expected_approved": True,
            "reasoning": (
                "Hook forte com estatistica de dor (9 em 10). CTA especifico com urgencia (meia-noite). "
                "Tamanho adequado para 30-45s. Prova social clara (2.400 alunos). "
                "Pequena deducao: hook poderia ser mais visual/sensorial para video."
            ),
        },
        {
            "input": (
                "Ola, somos a empresa XYZ e trabalhamos com solucoes financeiras ha 10 anos. "
                "Oferecemos consultoria personalizada para seu negocio. "
                "Entre em contato pelo nosso site para mais informacoes."
            ),
            "expected_score": 3,
            "expected_total": 3,
            "expected_approved": False,
            "reasoning": (
                "Sem hook (comeca com apresentacao de empresa). CTA generico ('entre em contato'). "
                "Texto longo para o valor entregue. Zero gatilhos persuasivos. "
                "Linguagem corporativa inapropriada para formato curto de Meta Ads."
            ),
        },
    ],
}
