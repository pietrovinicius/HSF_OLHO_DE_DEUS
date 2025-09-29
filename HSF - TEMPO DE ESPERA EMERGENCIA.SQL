WITH HistoricoMedia AS (
            -- 1. Calcula a média de tempo de espera dos últimos 90 dias para cada classificação.
            -- O tempo é calculado em minutos.
            SELECT
                TPA.NR_SEQ_CLASSIF,
                AVG((V.DT_ATEND_MEDICO - OBTER_DADOS_ATENDIMENTO_DT(V.NR_ATENDIMENTO, 'DFA')) * 24 * 60) AS MEDIA_MINUTOS_HISTORICO_3M
            FROM
                PEP_ATENDIMENTO_PS_V V
            JOIN TRIAGEM_PRONTO_ATEND TPA ON ( TPA.NR_ATENDIMENTO = V.NR_ATENDIMENTO )
            WHERE
                V.DT_ENTRADA >= SYSDATE - 90 -- Dados dos últimos 3 meses (90 dias)
                AND V.DT_ATEND_MEDICO IS NOT NULL -- Apenas atendimentos finalizados
                AND TPA.NR_SEQ_CLASSIF IN (3, 4, 5)
            GROUP BY
                TPA.NR_SEQ_CLASSIF
        )
        SELECT
            V.DT_ENTRADA,
            TPA.NR_SEQ_CLASSIF,
            SUBSTR(OBTER_DESC_TRIAGEM(TPA.NR_SEQ_CLASSIF), 1, 255) AS DS_TRIAGEM_CLASSIFICACAO,
            OBTER_NOME_PF(V.CD_PESSOA_FISICA) AS PACIENTE,
            V.NR_ATENDIMENTO,
            OBTER_DADOS_ATENDIMENTO_DT(V.NR_ATENDIMENTO, 'DE') DT_INI_ATEND_EUP,
            OBTER_DADOS_ATENDIMENTO_DT(V.NR_ATENDIMENTO, 'DFA') DT_FIM_ATEND_EUP,
            V.DT_ATEND_MEDICO,
            TO_CHAR(TRUNC(SYSDATE) + OBTER_MIN_ENTRE_DATAS(OBTER_DADOS_ATENDIMENTO_DT(V.NR_ATENDIMENTO, 'DFA'), V.DT_ATEND_MEDICO, 1) / (24 * 60), 'HH24:MI') AS TOTAL_ESPERA_ATEND,
            -- Novo campo com a média de tempo de espera por NR_SEQ_CLASSIF.
            -- Usamos NVL para definir '00:30' como padrão se o tempo médio não puder ser calculado.
            NVL(TO_CHAR(
                TRUNC(SYSDATE) + AVG(V.DT_ATEND_MEDICO - OBTER_DADOS_ATENDIMENTO_DT(V.NR_ATENDIMENTO, 'DFA')) OVER (PARTITION BY TPA.NR_SEQ_CLASSIF)
            , 'HH24:MI'), '00:30') AS TEMPO_MEDIO_CLASSIF,
            -- Novo campo para calcular o tempo de espera desde o fim do atendimento de enfermagem
            CASE
                WHEN V.DT_ATEND_MEDICO IS NOT NULL THEN '--'
                WHEN OBTER_DADOS_ATENDIMENTO_DT(V.NR_ATENDIMENTO, 'DFA') IS NULL THEN '--'
                ELSE TO_CHAR(TRUNC(SYSDATE) + (SYSDATE - OBTER_DADOS_ATENDIMENTO_DT(V.NR_ATENDIMENTO, 'DFA')), 'HH24:MI')
            END AS AGUARDANDO,
            -- 3. Traz a média histórica e garante que o valor mínimo seja 30 minutos.
            NVL(
                CASE
                    WHEN HM.MEDIA_MINUTOS_HISTORICO_3M < 30 THEN '00:30'
                    ELSE TO_CHAR(TRUNC(SYSDATE) + HM.MEDIA_MINUTOS_HISTORICO_3M / (24 * 60), 'HH24:MI')
                END,
                '00:30' -- Define '00:30' como padrão se não houver média histórica (NULL)
            ) AS MEDIA_HISTORICA_3M
        FROM
            PEP_ATENDIMENTO_PS_V V
        JOIN TRIAGEM_PRONTO_ATEND TPA ON ( TPA.NR_ATENDIMENTO = V.NR_ATENDIMENTO )
        -- 2. Junta os dados atuais com a média histórica calculada
        LEFT JOIN HistoricoMedia HM ON (TPA.NR_SEQ_CLASSIF = HM.NR_SEQ_CLASSIF)
        WHERE
            V.DT_CANCELAMENTO IS NULL
            AND TPA.NR_SEQ_CLASSIF IS NOT NULL
            AND V.CD_SETOR_ATENDIMENTO IN (75, 171)
            AND TPA.NR_SEQ_CLASSIF IN (3,4,5)
            AND V.DT_ENTRADA >= SYSDATE - INTERVAL '3' HOUR -- Mantém a janela de visualização de 3 horas
        ORDER BY
            V.DT_ENTRADA DESC