        SELECT 
            ATP.NR_SEQUENCIA AS ORDEM_SERVICO,
            UPPER(ATP.DS_DANO_BREVE) AS DESCRICAO,
            MAX(EXTRACT(YEAR FROM ATP.DT_ORDEM_SERVICO)) AS ANO_ORDEM_SERVICO,
            MAX(EXTRACT(MONTH FROM ATP.DT_ORDEM_SERVICO)) AS MES_ORDEM_SERVICO,
            MAX(EXTRACT(DAY FROM ATP.DT_ORDEM_SERVICO)) AS DIA_ORDEM_SERVICO,
            --TODO: fazer os mesmos extract com a ATP.DT_FIM_REAL
            MAX(EXTRACT(YEAR FROM ATP.DT_FIM_REAL)) AS ANO_ORDEM_SERVICO,
            MAX(EXTRACT(MONTH FROM ATP.DT_FIM_REAL)) AS MES_ORDEM_SERVICO,
            MAX(EXTRACT(DAY FROM ATP.DT_FIM_REAL)) AS DIA_ORDEM_SERVICO,

            MAX(EXTRACT(YEAR FROM MOSA.DT_ATIVIDADE)) AS ANO_ATIVIDADE,
            MAX(EXTRACT(MONTH FROM MOSA.DT_ATIVIDADE)) AS MES_ATIVIDADE,
            MAX(EXTRACT(DAY FROM MOSA.DT_ATIVIDADE)) AS DIA_ATIVIDADE,
            ROUND(sysdate - MAX(ATP.DT_ORDEM_SERVICO)) as IDADE_DA_OS,
            CASE WHEN ROUND(sysdate - MAX(ATP.DT_ORDEM_SERVICO)) > 2 THEN 'CRITICA'
                 ELSE 'NO PRAZO'
                 END AS ALERTA,
            MAX(MTOS.DS_TIPO) AS TIPO,
            MAX(DECODE(ATP.IE_STATUS_ORDEM, 1, 'Aberta', 2, 'Processo', 3, 'Encerrada')) AS STATUS,
            MAX(DECODE(ATP.IE_PRIORIDADE, 'A', 'Alta', 'M', 'Média', 'E','Emergência', 'Fora da Prioridade')) AS DS_PRIORIDADE,
            ABREVIA_NOME(INITCAP(OBTER_NOME_USUARIO(MOSA.NM_USUARIO_EXEC)),'A') AS ANALISTA,
            MAX(UPPER(OBTER_NOME_USUARIO(ATP.NM_USUARIO))) AS SOLICITANTE,
            SUM(NVL(MOSA.QT_MINUTO, 0)) AS MINUTOS_TOTAL,
            MAX(MGP.DS_GRUPO_PLANEJ) AS GRUPO_PLANEJAMENTO,
            ATP.NM_USUARIO AS LOGIN_RESPONSAVEL,
            ABREVIA_NOME(INITCAP(OBTER_NOME_USUARIO(ATP.NM_USUARIO)), 'A') AS NOME_RESPONSAVEL,
            (
                SELECT 
                    man_obter_desc_equip_os_par( 
                        e.nr_sequencia ,
                        obter_valor_param_usuario(299, 479, obter_perfil_ativo, obter_usuario_ativo, obter_estabelecimento_ativo) 
                    ) DS 
                FROM man_equipamento e 
                WHERE e.nr_sequencia = ATP.NR_SEQ_EQUIPAMENTO
            ) AS EQUIPAMENTO
        FROM MAN_ORDEM_SERVICO ATP
        LEFT JOIN MAN_GRUPO_PLANEJAMENTO MGP ON MGP.NR_SEQUENCIA = ATP.NR_GRUPO_PLANEJ
        LEFT JOIN MAN_ORDEM_SERV_ATIV MOSA ON MOSA.NR_SEQ_ORDEM_SERV = ATP.NR_SEQUENCIA
        LEFT JOIN MAN_TIPO_ORDEM_SERVICO MTOS ON MTOS.NR_SEQUENCIA = ATP.NR_SEQ_TIPO_ORDEM
        WHERE 1 = 1
            AND MGP.NR_SEQUENCIA = 22
            AND ATP.IE_STATUS_ORDEM = 3
            AND ATP.DT_FIM_REAL IS NOT NULL
            AND EXTRACT(YEAR FROM ATP.DT_FIM_REAL) = EXTRACT(YEAR FROM SYSDATE)
            AND EXTRACT(MONTH FROM ATP.DT_FIM_REAL)= EXTRACT(MONTH FROM SYSDATE)
            AND EXTRACT(DAY FROM ATP.DT_FIM_REAL)= EXTRACT(DAY FROM SYSDATE)
            
            --AND (
            --    ATP.NR_SEQ_EQUIPAMENTO = 752 
            --    OR LOWER(ATP.NM_USUARIO) IN (
            --        'aslalmeida', 'clamaral', 'dafdmalmeida', 'icrjunior', 
            --        'iffialho', 'pvplima', 'kloliveira', 'tgananca', 
            --        'lgspacheco', 'dlsrosario', 'ggapinto', 'nsmedeiros', 'smsfilho'
            --    )
            --    OR UPPER(OBTER_NOME_USUARIO(ATP.NM_USUARIO)) = UPPER(OBTER_NOME_USUARIO(ATP.NM_USUARIO))
            --)
            AND UPPER(OBTER_NOME_USUARIO(ATP.NM_USUARIO)) = UPPER(OBTER_NOME_USUARIO(ATP.NM_USUARIO))
        GROUP BY 
            ATP.NR_SEQUENCIA, 
            UPPER(ATP.DS_DANO_BREVE),
            ABREVIA_NOME(INITCAP(OBTER_NOME_USUARIO(MOSA.NM_USUARIO_EXEC)),'A'),
            ATP.NM_USUARIO,
            ATP.NR_SEQ_EQUIPAMENTO,
            ATP.DT_FIM_REAL
        ORDER BY 3 DESC, 4 DESC, 5 DESC