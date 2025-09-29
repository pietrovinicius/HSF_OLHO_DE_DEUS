--29/09/2025
--@PLima
--REL_1500_Tempo_espera_Paciente_Excel
select
    EXTRACT(YEAR FROM a.dt_inicio_atendimento) ano,
    EXTRACT(MONTH FROM a.dt_inicio_atendimento) mes,
    EXTRACT(DAY FROM a.dt_inicio_atendimento) dia,
    substr(obter_nome_setor(c.cd_setor_atendimento),1,50) setor_atendimento,
    to_char(a.dt_recebimento_senha,'DD/MM/YYYY hh24:mi:ss') inicio,   
    to_char(b.dt_fim_atendimento,'DD/MM/YYYY hh24:mi:ss') fim,
    OBTER_DIF_HORARIO(b.DT_GERACAO_SENHA,b.dt_fim_atendimento) total_Recep,
    abrevia_nome_pf(Obter_Dados_Usuario_Opcao(c.nm_usuario_atend,'C'),'A') nm_usuario_atend,    
    c.NR_ATENDIMENTO nr_atendimento,
    ABREVIA_NOME(OBTER_NOME_PACIENTE(c.NR_ATENDIMENTO), 'A') AS PACIENTE,
    c.DS_STATUS_PACIENTE status,
    to_char(c.DT_ENTRADA,'DD/MM/YYYY hh24:mi:ss') internacao,
    to_char(c.DT_ALTA,'DD/MM/YYYY hh24:mi:ss') alta,
    to_char(C.DT_NASCIMENTO,'DD/MM/YYYY') nascimento,
    obter_idade(c.dt_nascimento,sysdate,'S') idade,
    somente_numero(SUBSTR(obter_idade(c.dt_nascimento, SYSDATE, 'A'),1,40)) idade_nr_anos,
    C.IE_SEXO,
    initcap(f.ds_fila) ds_fila,
    initcap(m.ds_local) ds_local, 
    substr(substr(obter_letra_verifacao_senha(nvl(b.nr_seq_fila_senha_origem, b.nr_seq_fila_senha)),1,1) ||' '|| b.cd_senha_gerada,1,255) cd_senha,
    initcap(Obter_Nome_Convenio(Obter_Convenio_Atendimento(a.nr_atendimento))) convenio,
    --abrevia_nome_pf(Obter_Dados_Usuario_Opcao(b.nm_usuario_chamada,'C'),'A') nm_usuario_chamada,
    obter_valor_dominio(17,a.ie_clinica) especialidade,
    initcap(c.NM_MEDICO) nm_medico,
    --initcap(c.nm_medico_conselho) nm_medico_conselho,
    to_char(b.dt_fim_atendimento,'DD/MM/YYYY hh24:mi:ss') as paciente_senha_fila_fim,
    to_char(a.dt_inicio_atendimento,'DD/MM/YYYY hh24:mi:ss') as atendimento_paciente_dt_inicio,
    OBTER_DIF_HORARIO(b.dt_fim_atendimento,a.dt_inicio_atendimento) as  tempo_espera_atend,
    to_char(a.dt_inicio_atendimento,'DD/MM/YYYY hh24:mi:ss') ini_atend,
    to_char(a.dt_fim_consulta,'DD/MM/YYYY hh24:mi:ss') fim_atend,
    c.CD_CID_PRINCIPAL,
    OBTER_DIF_HORARIO(a.dt_inicio_atendimento,a.dt_fim_consulta) as total_medico_atend,
    TO_CHAR(tpa.dt_inicio_triagem,'DD/MM/YYYY hh24:mi:ss') AS dt_inicio_triagem,
    TO_CHAR(tpa.dt_fim_triagem,'DD/MM/YYYY hh24:mi:ss') AS dt_fim_triagem,
    SUBSTR(obter_desc_triagem(tpa.nr_seq_classif), 1, 255) AS triagem_classificacao,
    TRUNC((tpa.dt_fim_triagem - tpa.dt_inicio_triagem) * 24 * 60) || ' minuto(s) e ' ||
    MOD(TRUNC((tpa.dt_fim_triagem - tpa.dt_inicio_triagem) * 24 * 60 * 60), 60) || ' segundo(s)' AS triagem_minutos
    ,c.DS_NIVEL_URGENCIA    as nivel_urgencia
from atendimento_paciente a
left join paciente_senha_fila b on ( a.NR_SEQ_PAC_SENHA_FILA = b.nr_sequencia )
left join atendimento_paciente_v c on ( c.nr_atendimento = a.nr_atendimento )
left join fila_espera_senha f on ( b.nr_seq_fila_senha = f.nr_sequencia )
left join maquina_local_senha m on ( b.nr_seq_local_senha = m.nr_sequencia )
left join triagem_pronto_atend tpa on ( tpa.NR_ATENDIMENTO = a.NR_ATENDIMENTO )
where 1 = 1
and   c.cd_setor_atendimento in (3,75,80,171)
and EXTRACT(YEAR FROM a.dt_inicio_atendimento) = EXTRACT(YEAR FROM SYSDATE) --and--{ano}
and EXTRACT(MONTH FROM a.dt_inicio_atendimento) = EXTRACT(MONTH FROM SYSDATE) --{mes}
and EXTRACT(DAY FROM a.dt_inicio_atendimento) = EXTRACT(DAY FROM SYSDATE) --{dia}
--TODO: retornar apenas atendimentos da última hora
--and a.dt_inicio_atendimento >= sysdate - 1/24

order by a.dt_recebimento_senha desc
--FETCH FIRST 100 ROWS ONLY