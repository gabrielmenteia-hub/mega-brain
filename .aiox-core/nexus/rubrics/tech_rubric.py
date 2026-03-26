"""Technical quality rubric for NEXUS review agents.

Evaluates video ad technical quality across 4 dimensions:
visual_quality, audio_quality, sync, and format_compliance.

Threshold for approval: min_tech_score = 6 (NexusConfig default)
"""

TECH_RUBRIC = {
    "dimension": "tech",
    "description": (
        "Avalia a qualidade tecnica do video publicitario para veiculacao no Meta Ads. "
        "Foco em clareza visual, qualidade de audio, sincronizacao e conformidade de formato."
    ),
    "criteria": [
        {
            "name": "visual_quality",
            "weight": 0.3,
            "description": "Clareza visual, resolucao, iluminacao e composicao do video.",
            "levels": {
                10: "Imagem nítida em full HD+, iluminacao profissional, composicao equilibrada e product placement perfeito.",
                8: "Boa resolucao e iluminacao adequada. Pequenas imperfeicoes que nao prejudicam a leitura.",
                6: "Qualidade aceitavel para veiculacao. Iluminacao ou composicao levemente abaixo do ideal.",
                4: "Problemas visiveis: iluminacao ruim, desfoque parcial ou enquadramento amador.",
                2: "Video com qualidade tecnica inadequada para anuncio: pixelado, muito escuro ou tremido.",
            },
        },
        {
            "name": "audio_quality",
            "weight": 0.3,
            "description": "Clareza de voz, volume adequado e ausencia de ruido de fundo.",
            "levels": {
                10: "Audio cristalino, volume consistente, sem ruido. Dicao clara e ritmo ideal para o formato.",
                8: "Audio claro com pequeno ruido de fundo que nao compromete a compreensao.",
                6: "Audio inteligivel mas com algum ruido ou variacao de volume perceptivel.",
                4: "Dificuldade para entender parte da fala. Ruido de fundo distrai ou volume inconsistente.",
                2: "Audio ininteligivel, ausente ou com problema grave (eco extremo, distorcao, corte).",
            },
        },
        {
            "name": "sync",
            "weight": 0.2,
            "description": "Sincronizacao audio-video, lip sync e timing de elementos graficos.",
            "levels": {
                10: "Sincronia perfeita entre audio e video. Graficos e legendas aparecem no momento exato.",
                8: "Sync adequado com atraso imperceptivel ou grafico levemente atrasado sem impacto.",
                6: "Leve dessincronizacao perceptivel mas nao distratora. Lip sync aceitavel.",
                4: "Dessincronizacao notavel que compromete a credibilidade ou distrai o espectador.",
                2: "Audio e video completamente fora de sync ou ausencia de sincronizacao em elementos criticos.",
            },
        },
        {
            "name": "format_compliance",
            "weight": 0.2,
            "description": "Duracao, aspect ratio e resolucao minima conforme especificacoes Meta Ads.",
            "levels": {
                10: "Formato perfeito: aspect ratio 9:16 ou 4:5, resolucao >= 1080p, duracao entre 15-60s para Stories/Reels.",
                8: "Formato correto com pequeno desvio aceitavel (ex: 720p em 9:16, ou duracao de 65s).",
                6: "Formato parcialmente adequado: resolucao minima atingida mas aspect ratio subotimo.",
                4: "Formato com problema significativo: resolucao abaixo do minimo ou duracao fora da faixa ideal.",
                2: "Formato incompativel: aspect ratio errado (ex: 16:9 em Stories), resolucao abaixo de 480p ou duracao > 120s.",
            },
        },
    ],
    "few_shot_examples": [
        {
            "input": (
                "Video gravado em iPhone 14, iluminacao natural boa, resolucao 4K downscalada para 1080p. "
                "Audio gravado com microfone lapela, sem ruido de fundo. "
                "Formato 9:16 vertical, 45 segundos. Legendas sincronizadas."
            ),
            "expected_score": 9,
            "expected_total": 9,
            "expected_approved": True,
            "reasoning": (
                "Excelente qualidade visual e de audio. Formato ideal para Reels. "
                "Legendas sincronizadas corretamente. Leve deducao por nao ser producao profissional "
                "mas qualidade tecnica consistentemente alta."
            ),
        },
        {
            "input": (
                "Video gravado com webcam antiga em ambiente escuro. "
                "Audio captado pelo microfone do computador com eco e vento ao fundo. "
                "Formato 16:9 (landscape), resolucao 480p, duracao de 3 minutos."
            ),
            "expected_score": 2,
            "expected_total": 2,
            "expected_approved": False,
            "reasoning": (
                "Qualidade visual inadequada: resolucao baixa e iluminacao ruim. "
                "Audio com ruido grave (eco + vento). Formato landscape incompativel com Stories/Reels. "
                "Duracao de 3 minutos muito acima do limite de 60s para o formato. "
                "Todas as dimensoes tecnicas abaixo do minimo aceitavel."
            ),
        },
    ],
}
