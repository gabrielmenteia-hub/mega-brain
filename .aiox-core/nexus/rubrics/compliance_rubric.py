"""Meta Ads compliance rubric for NEXUS review agents.

Evaluates ad compliance with Meta advertising policies across 4 dimensions:
prohibited_content, targeting_alignment, disclosure, and community_standards.

Threshold for approval: min_compliance_score = 8 (NexusConfig default — most strict)
"""

COMPLIANCE_RUBRIC = {
    "dimension": "compliance",
    "description": (
        "Avalia conformidade do anuncio com as politicas de publicidade do Meta Ads. "
        "Threshold mais alto (8) por risco de bloqueio de conta e rejeicao automatica."
    ),
    "criteria": [
        {
            "name": "prohibited_content",
            "weight": 0.3,
            "description": (
                "Ausencia de claims medicos, financeiros garantidos, enganosos ou proibidos "
                "pelas politicas do Meta Ads."
            ),
            "levels": {
                10: "Zero claims problematicos. Linguagem cautelosa com 'pode', 'tende', 'resultados variam'. Totalmente seguro.",
                8: "Sem claims proibidos. Linguagem levemente assertiva mas dentro dos limites aceitaveis pelo Meta.",
                6: "Claims bordeline que podem acionar revisao manual mas provavelmente serao aprovados.",
                4: "Um claim problematico presente (ex: garantia de resultado financeiro especifico) — alto risco de rejeicao.",
                2: "Claims claramente proibidos: cura de doenca, retorno financeiro garantido, conteudo enganoso explicito.",
            },
        },
        {
            "name": "targeting_alignment",
            "weight": 0.2,
            "description": "Linguagem e oferta adequadas ao publico-alvo declarado sem discriminacao proibida.",
            "levels": {
                10: "Linguagem perfeitamente alinhada ao avatar. Nenhuma referencia que possa caracterizar discriminacao.",
                8: "Alinhamento bom com pequena inconsistencia de linguagem ou publico.",
                6: "Mensagem generica que serve ao publico mas nao foi otimizada para o avatar.",
                4: "Linguagem inapropriada para o publico ou sugestao implicita de discriminacao por raca/genero/religiao.",
                2: "Discriminacao explicita ou linguagem claramente inadequada para o segmento anunciado.",
            },
        },
        {
            "name": "disclosure",
            "weight": 0.2,
            "description": "Presenca de disclaimers obrigatorios quando necessarios (resultados, parcerias, financeiro).",
            "levels": {
                10: "Todos os disclaimers necessarios presentes e posicionados de forma legivel e prominente.",
                8: "Disclaimers presentes mas com pequeno problema de posicionamento ou tamanho.",
                6: "Disclaimer obrigatorio presente mas dificil de ler ou incompleto.",
                4: "Disclaimer ausente em contexto onde seria necessario (ex: antes/depois sem aviso de resultados variam).",
                2: "Total ausencia de disclosure em contexto de alto risco (claims de saude, financeiro ou testemunho).",
            },
        },
        {
            "name": "community_standards",
            "weight": 0.3,
            "description": "Respeito as normas da comunidade Meta: sem conteudo sensivel, violento ou sexualizado.",
            "levels": {
                10: "Conteudo totalmente seguro para todas as audiences. Apropriado para todos os publicos.",
                8: "Conteudo adequado com elemento bordeline (ex: imagem de bebida alcoolica) — requer segmentacao correta.",
                6: "Conteudo com elementos sensiveis que exigem configuracoes de segmentacao restritas.",
                4: "Conteudo que provavelmente acionara revisao manual por sensibilidade ou violencia implicita.",
                2: "Conteudo claramente violador: nudez, violencia explicita, discurso de odio ou conteudo para adultos sem restricao.",
            },
        },
    ],
    "few_shot_examples": [
        {
            "input": (
                "Aprenda a organizar suas financas em 30 dias com o Metodo Clareza. "
                "Mais de 5.000 alunos ja transformaram sua relacao com o dinheiro. "
                "Resultados podem variar. Clique e comece hoje."
            ),
            "expected_score": 9,
            "expected_total": 9,
            "expected_approved": True,
            "reasoning": (
                "Sem claims financeiros garantidos. Usa 'transformaram' (resultado qualitativo, nao garantido). "
                "Disclaimer 'resultados podem variar' presente. Linguagem adequada para educacao financeira. "
                "Sem conteudo sensivel. Pequena deducao por 'Aprenda ... em 30 dias' que pode ser interpretado "
                "como garantia de prazo, mas dentro dos limites aceitaveis."
            ),
        },
        {
            "input": (
                "Investimento garantido com retorno de 30% ao mes! "
                "Nossa formula secreta NUNCA falha. Centenas de clientes ja ficaram ricos. "
                "Nao perca essa oportunidade unica — vagas MUITO limitadas!"
            ),
            "expected_score": 1,
            "expected_total": 1,
            "expected_approved": False,
            "reasoning": (
                "Multiplas violacoes graves: 'retorno garantido de 30%' (claim financeiro proibido), "
                "'formula NUNCA falha' (claim enganoso), 'vagas muito limitadas' sem evidencia (escassez falsa). "
                "Alto risco de bloqueio de conta. Sem disclaimers. "
                "Conteudo claramente enganoso que viola politicas de publicidade financeira do Meta."
            ),
        },
    ],
}
