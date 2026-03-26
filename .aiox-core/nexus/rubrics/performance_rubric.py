"""Performance prediction rubric for NEXUS review agents.

Evaluates predicted ad performance on Meta Ads across 4 dimensions:
scroll_stopping, engagement_potential, click_intent, and audience_match.

Threshold for approval: min_performance_score = 6 (NexusConfig default)
"""

PERFORMANCE_RUBRIC = {
    "dimension": "performance",
    "description": (
        "Prediz a performance do anuncio no Meta Ads com base em padroes de criativos "
        "de alto desempenho. Foco em scroll-stopping, engajamento, intencao de clique "
        "e aderencia ao avatar/nicho."
    ),
    "criteria": [
        {
            "name": "scroll_stopping",
            "weight": 0.3,
            "description": (
                "Probabilidade de parar o scroll nos primeiros 3 segundos do video. "
                "Elemento visual ou auditivo de impacto imediato."
            ),
            "levels": {
                10: "Abertura com elemento de choque visual, movimento brusco, texto grande ou som impactante nos primeiros 2s.",
                8: "Abertura forte com rosto/expressao marcante, pergunta provocativa ou situacao de tensao.",
                6: "Abertura razoavel que pode reter espectadores ja predispostos ao tema, mas nao é universalmente atrativa.",
                4: "Abertura lenta: fala calma, texto estatico ou produto sozinho sem contexto nos primeiros 3s.",
                2: "Abertura que ativamente repele: tela preta, intro longa, musica de espera ou logo animado.",
            },
        },
        {
            "name": "engagement_potential",
            "weight": 0.25,
            "description": "Probabilidade de gerar comentarios, compartilhamentos ou saves organicos.",
            "levels": {
                10: "Conteudo que provoca opiniao forte, resolve duvida frequente ou e altamente compartilhavel por identidade.",
                8: "Conteudo que estimula comentarios (pergunta final, afirmacao polarizadora) ou e util o suficiente para salvar.",
                6: "Conteudo que pode gerar algum engajamento mas nao tem elemento especifico que estimule acao social.",
                4: "Conteudo passivo: assistido e esquecido. Sem gancho para comentar, compartilhar ou salvar.",
                2: "Conteudo que pode gerar reacoes negativas (comentarios de critica) ou que ninguem compartilharia.",
            },
        },
        {
            "name": "click_intent",
            "weight": 0.25,
            "description": "Forca da motivacao para clicar no CTA ou interagir com o anuncio.",
            "levels": {
                10: "Urgencia genuina + beneficio claro + fricao minima para clicar. Fluxo natural do video para o CTA.",
                8: "CTA com beneficio claro e alguma urgencia. Espectador motivado a clicar apos assistir.",
                6: "CTA presente mas motivacao para clicar depende de predisposicao previa do espectador.",
                4: "CTA fraco ou desconectado do conteudo. Pouca motivacao para agir.",
                2: "Sem CTA funcional ou CTA que gera confusao sobre a proxima acao.",
            },
        },
        {
            "name": "audience_match",
            "weight": 0.2,
            "description": "Aderencia do conteudo ao avatar/nicho especificado. Relevancia percebida pelo publico-alvo.",
            "levels": {
                10: "Linguagem, referencias e dores do anuncio sao identicas ao universo do avatar. Parece feito exclusivamente para ele.",
                8: "Alta relevancia com pequena inconsistencia de linguagem ou referencia cultural.",
                6: "Relevante para o nicho mas com linguagem generica que nao ressoa com especificidade.",
                4: "Apenas parcialmente relevante. Dores ou beneficios tangencialmente relacionados ao avatar.",
                2: "Conteudo inadequado para o nicho: linguagem, exemplos ou produto claramente para outro publico.",
            },
        },
    ],
    "few_shot_examples": [
        {
            "input": (
                "VOCE esta cometendo ESSE erro todo dia? [pausa dramatica com texto na tela] "
                "Empreendedores que faturam acima de 100k por mes nunca fazem isso. "
                "Descobri isso apos perder R$ 80 mil em 6 meses. "
                "Se voce gerencia time remoto, precisa ver isso. Link nos comentarios."
            ),
            "expected_score": 8,
            "expected_total": 8,
            "expected_approved": True,
            "reasoning": (
                "Abertura com pergunta provocativa e pausa — alto scroll-stopping. "
                "Afirmacao polarizadora sobre empreendedores de alto faturamento gera comentarios. "
                "Historia de perda cria conexao emocional e motivacao para clicar. "
                "Nicho especifico (gestao remota) aumenta relevancia. "
                "Pequena deducao: CTA 'link nos comentarios' e menos direto que o ideal."
            ),
        },
        {
            "input": (
                "Ola! Somos uma empresa de software de gestao. "
                "Nosso sistema ajuda empresas a organizarem processos. "
                "Temos varias funcionalidades. Acesse nosso site para conhecer nossos planos."
            ),
            "expected_score": 2,
            "expected_total": 2,
            "expected_approved": False,
            "reasoning": (
                "Abertura com 'Ola!' e apresentacao de empresa — scroll-stopping minimo. "
                "Conteudo totalmente generico sem dor especifica ou beneficio concreto. "
                "Sem elemento que estimule comentario ou compartilhamento. "
                "CTA generico para 'nosso site' sem motivacao clara. "
                "Nenhuma especificidade de nicho — poderia ser qualquer empresa para qualquer publico."
            ),
        },
    ],
}
