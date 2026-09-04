import streamlit as st
import pandas as pd
from fpdf import FPDF
import unicodedata
import pickle
import os

st.set_page_config(layout="wide", page_title="Conciliador Pix Interativo")

st.title("⚡ Conciliador Web de Pix Otimizado")
st.markdown("### Processamento de Alta Performance com Renderização Otimizada")

# --- SISTEMA DE AUTO-SAVE DIVIDIDO ---
CACHE_DADOS = "backup_dados.pkl"       
CACHE_PROGRESSO = "backup_progresso.pkl" 

def salvar_dados_pesados():
    dados = {
        "processado": st.session_state.processado,
        "auto_matches": st.session_state.auto_matches,
        "unmatched_banco": st.session_state.unmatched_banco,
        "unmatched_sistema": st.session_state.unmatched_sistema,
        "last_files": st.session_state.get("last_files") 
    }
    try:
        with open(CACHE_DADOS, "wb") as f: pickle.dump(dados, f)
    except: pass

def salvar_progresso_leve():
    dados = {
        "vinculos_manuais": st.session_state.vinculos_manuais,
        "validados": st.session_state.validados
    }
    try:
        with open(CACHE_PROGRESSO, "wb") as f: pickle.dump(dados, f)
    except: pass

def limpar_progresso():
    for arquivo in [CACHE_DADOS, CACHE_PROGRESSO]:
        if os.path.exists(arquivo):
            try: os.remove(arquivo)
            except: pass

# --- INICIALIZAÇÃO E RECUPERAÇÃO DE DADOS ---
recuperado = False
if "processado" not in st.session_state:
    if os.path.exists(CACHE_DADOS) and os.path.exists(CACHE_PROGRESSO):
        try:
            with open(CACHE_DADOS, "rb") as f:
                dados_pesados = pickle.load(f)
                for key, val in dados_pesados.items(): st.session_state[key] = val
            with open(CACHE_PROGRESSO, "rb") as f:
                dados_leves = pickle.load(f)
                for key, val in dados_leves.items(): st.session_state[key] = val
            recuperado = True
        except:
            pass
            
    if not recuperado:
        st.session_state.processado = False
        st.session_state.auto_matches = []
        st.session_state.unmatched_banco = []
        st.session_state.unmatched_sistema = []
        st.session_state.vinculos_manuais = {}  
        st.session_state.validados = set()      
        st.session_state.last_files = None

# --- CALLBACKS CORRIGIDOS E ULTRA RÁPIDOS ---
def alternar_validacao(idx_b):
    chk_key = f"chk_v_{idx_b}"
    if st.session_state.get(chk_key, False):
        st.session_state.validados.add(idx_b)
    else:
        st.session_state.validados.discard(idx_b)
    salvar_progresso_leve() 

def desfazer_vinculo_seguro(idx_b):
    if idx_b in st.session_state.vinculos_manuais:
        del st.session_state.vinculos_manuais[idx_b]
    st.session_state.validados.discard(idx_b)
    st.session_state[f"chk_v_{idx_b}"] = False
    st.session_state[f"ver_det_{idx_b}"] = False
    salvar_progresso_leve()

def confirmar_vinculo_seguro(idx_b):
    # Obtém a seleção diretamente da chave da caixa de multisseleção
    selecionados = st.session_state.get(f"ms_link_{idx_b}", [])
    if selecionados:
        st.session_state.vinculos_manuais[idx_b] = [int(x) for x in selecionados]
        st.session_state.validados.add(idx_b)
        st.session_state[f"chk_v_{idx_b}"] = True
        st.session_state[f"ver_det_{idx_b}"] = False
        salvar_progresso_leve()

# --- FUNÇÕES AUXILIARES ---
def limpar_acentos(texto):
    text = str(texto).replace("•", "-")
    return "".join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn').encode('latin-1', 'ignore').decode('latin-1')

def obter_pagador(dados_s):
    pag = dados_s.get('Pagador')
    if pd.isna(pag) or str(pag).strip().lower() in ['nan', '', 'none']: return "Não encontrado pagador no sistema"
    return str(pag).strip()

def obter_passageiro(dados_s):
    pas = dados_s.get('Passageiro')
    if pd.isna(pas) or str(pas).strip().lower() in ['nan', '', 'none']: return "Não encontrado passageiro no sistema"
    return str(pas).strip()

def converter_valor_sistema(val):
    try:
        if pd.isna(val): return 0.0
        if isinstance(val, (int, float)): return float(val)
        return float(str(val).strip().replace('.', '').replace(',', '.'))
    except: return 0.0

def converter_data_banco(val):
    try:
        partes = str(val).split("•")
        data_pt = partes[0].strip()
        hora_pt = partes[1].strip().replace("h", ":").replace("m", ":").replace("s", "")
        dia, mes_nome = data_pt.split("/")
        meses = {"jan":"01","fev":"02","mar":"03","abr":"04","mai":"05","jun":"06","jul":"07","ago":"08","set":"09","out":"10","nov":"11","dez":"12"}
        return pd.to_datetime(f"{dia}/{meses.get(mes_nome.lower()[:3], '06')}/2026 {hora_pt}", format="%d/%m/%Y %H:%M:%S")
    except: return None

if st.session_state.processado and recuperado:
    st.info("💾 **Sessão Restaurada:** Seus dados e vínculos anteriores foram carregados automaticamente.")

col_up1, col_up2 = st.columns(2)
with col_up1: file_sistema = st.file_uploader("📂 Relatório Pix do Sistema (.xlsx)", type=["xlsx"])
with col_up2: file_banco = st.file_uploader("📂 Relatório Pix do Banco (.xls ou .xlsx)", type=["xls", "xlsx"])

# SENSOR AUTOMÁTICO DE NOVOS ARQUIVOS
if file_sistema and file_banco:
    arquivos_atuais = f"{file_sistema.name} + {file_banco.name}"
    if st.session_state.get("last_files") != arquivos_atuais:
        limpar_progresso()
        st.session_state.processado = False
        st.session_state.vinculos_manuais = {}
        st.session_state.validados = set()
        st.session_state.last_files = arquivos_atuais

# 🚀 BOTÃO "INICIAR CONCILIAÇÃO"
if file_sistema and file_banco and not st.session_state.processado:
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("🚀 INICIAR CONCILIAÇÃO", type="primary", use_container_width=True):
            with st.spinner("Analisando e cruzando dados. Aguarde um instante..."):
                df_sistema = pd.read_excel(file_sistema, header=2)
                df_banco = pd.read_excel(file_banco)
                
                if 'Num Passagem' in df_sistema.columns:
                    df_sistema = df_sistema[df_sistema['Num Passagem'].notna()]
                    df_sistema = df_sistema[~df_sistema['Num Passagem'].astype(str).str.contains('Num Passa|Num Passagem|Bilhete', case=False, na=False)]
                if 'Valor' in df_sistema.columns:
                    df_sistema = df_sistema[df_sistema['Valor'].notna()]
                    df_sistema = df_sistema[~df_sistema['Valor'].astype(str).str.contains('Valor', case=False, na=False)]
                
                df_sistema['dt_parsed'] = pd.to_datetime(df_sistema['Data Venda'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
                df_banco['dt_parsed'] = df_banco['dataEHora'].apply(converter_data_banco)
                
                sistema_records = df_sistema.to_dict('records')
                banco_records = df_banco.to_dict('records')
                
                s_list_prep = []
                for idx_s, row_s in enumerate(sistema_records):
                    s_list_prep.append({
                        "idx_s": idx_s, "linha_excel": idx_s + 4, 
                        "nsu_s": str(row_s.get('Nsu', '')).strip() if pd.notna(row_s.get('Nsu')) else "", 
                        "aut_s": str(row_s.get('Autorizacao', '')).strip() if pd.notna(row_s.get('Autorizacao')) else "",
                        "dados": row_s, "dt_parsed": row_s.get('dt_parsed'), "valor_clean": converter_valor_sistema(row_s.get('Valor', 0))
                    })
                
                auto_matches = []
                unmatched_banco = []
                linhas_sistema_com_match = set()
                
                for idx_b, row_b in enumerate(banco_records):
                    id_b = str(row_b.get('idOperacao', '')).strip() if pd.notna(row_b.get('idOperacao')) else ""
                    tx_b = str(row_b.get('txId', '')).strip() if pd.notna(row_b.get('txId')) else ""
                    
                    passagens = []
                    if id_b or tx_b:
                        for item_s in s_list_prep:
                            if item_s["nsu_s"] and item_s["aut_s"] and id_b.startswith(item_s["nsu_s"]) and tx_b.startswith(item_s["aut_s"]):
                                passagens.append({"idx_s": item_s["idx_s"], "linha_excel": item_s["linha_excel"], "dados": item_s["dados"]})
                                linhas_sistema_com_match.add(item_s["idx_s"])
                            
                    if passagens: auto_matches.append({"idx_b": idx_b, "banco": row_b, "passagens": passagens})
                    else: unmatched_banco.append({"idx_b": idx_b, "banco": row_b, "dt_parsed": row_b.get('dt_parsed')})
                        
                unmatched_sistema = [item_s for item_s in s_list_prep if item_s["idx_s"] not in linhas_sistema_com_match]
                        
                st.session_state.auto_matches = auto_matches
                st.session_state.unmatched_banco = unmatched_banco
                st.session_state.unmatched_sistema = unmatched_sistema
                st.session_state.processado = True
                
                salvar_dados_pesados()
                salvar_progresso_leve()
                st.rerun()

# RENDERIZAÇÃO DA INTERFACE WEB
if st.session_state.processado:
    
    if st.button("♻️ Limpar Memória e Recomeçar", use_container_width=True):
        limpar_progresso()
        st.session_state.processado = False
        st.session_state.vinculos_manuais = {}
        st.session_state.validados = set()
        st.rerun()
        
    linhas_sistema_usadas_manualmente = set()
    for s_list in st.session_state.vinculos_manuais.values():
        linhas_sistema_usadas_manualmente.update(s_list)
        
    grupo_conciliados = []  
    grupo_erros_banco = []  
    grupo_erros_sistema = [] 
    
    for match in st.session_state.auto_matches:
        grupo_conciliados.append({"idx_b": match["idx_b"], "banco": match["banco"], "passagens": match["passagens"], "metodo": "Automático"})
        
    for b_item in st.session_state.unmatched_banco:
        idx_b = b_item["idx_b"]
        if idx_b in st.session_state.vinculos_manuais:
            passagens_manuais = []
            for idx_s in st.session_state.vinculos_manuais[idx_b]:
                dados_s = next((s for s in st.session_state.unmatched_sistema if int(s["idx_s"]) == int(idx_s)), None)
                if dados_s: passagens_manuais.append({"idx_s": dados_s["idx_s"], "linha_excel": dados_s["linha_excel"], "dados": dados_s["dados"]})
            grupo_conciliados.append({"idx_b": idx_b, "banco": b_item["banco"], "passagens": passagens_manuais, "metodo": "Manual"})
        else:
            grupo_erros_banco.append(b_item)
            
    for s_item in st.session_state.unmatched_sistema:
        if s_item["idx_s"] not in linhas_sistema_usadas_manualmente:
            grupo_erros_sistema.append(s_item)
            
    # --- INDICADORES ---
    st.markdown("### 📊 Painel Geral de Auditoria")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🟢 Total Conciliados", len(grupo_conciliados))
    m2.metric("✅ Validados p/ Você", len(st.session_state.validados))
    m3.metric("🔴 Pix s/ Passagem (Banco)", len(grupo_erros_banco))
    m4.metric("⚠️ Passagens Pendentes (Sistema)", len(grupo_erros_sistema))
    
    st.markdown("---")
    st.subheader("🟢 Lançamentos Conciliados")
    
    col_h_sw, col_h_content = st.columns([1, 15])
    with col_h_sw: st.markdown("**Valida**")
    with col_h_content: st.markdown("**Dados do Lançamento Cruzado**")
    st.markdown("<hr style='margin: 0px 0px 8px 0px; border-color: #CBD5E1;'>", unsafe_allow_html=True)
    
    for item in grupo_conciliados:
        idx_b = item["idx_b"]
        is_valid = idx_b in st.session_state.validados
            
        b = item["banco"]
        chk_key = f"chk_v_{idx_b}"
        if chk_key not in st.session_state: st.session_state[chk_key] = is_valid
        
        texto_linhas = ", ".join(str(p["linha_excel"]) for p in item["passagens"])
        
        if is_valid:
            col_sw, col_txt, col_btn = st.columns([1, 10, 2])
            with col_sw: st.checkbox("Validar", key=chk_key, on_change=alternar_validacao, args=(idx_b,), label_visibility="collapsed")
            with col_txt: st.markdown(f"✅ **[VALIDADO]** R$ {b.get('valor', 0):,.2f} | {b.get('origemDestinatario', '---')} -> Linha(s) Sistema: **{texto_linhas}**")
            with col_btn:
                if st.button("👁️ Detalhes", key=f"btn_det_{idx_b}", use_container_width=True):
                    st.session_state[f"ver_det_{idx_b}"] = True
                    st.rerun()
            
            if st.session_state.get(f"ver_det_{idx_b}", False):
                with st.container(border=True):
                    col_b, col_m, col_l = st.columns([4, 3, 5])
                    with col_b:
                        st.caption(f"🗓️ **Data/Hora:** {b.get('dataEHora')}")
                        st.caption(f"👤 **Origem:** {b.get('origemDestinatario')}")
                    with col_m:
                        if st.button("Ocultar", key=f"btn_ocu_{idx_b}"):
                            st.session_state[f"ver_det_{idx_b}"] = False
                            st.rerun()
                        # 👇 AGORA O BOTÃO APARECE MESMO SE ESTIVER VALIDADO (SE FOR MANUAL)
                        if item["metodo"] == "Manual": 
                            st.button("Desfazer Vínculo", key=f"btn_unl_val_{idx_b}", on_click=desfazer_vinculo_seguro, args=(idx_b,))
                    with col_l:
                        for p in item["passagens"]: 
                            st.caption(f"📋 Linha: {p['linha_excel']} | Bilhete: {p['dados'].get('Num Passagem')} | Pas: {obter_passageiro(p['dados'])}")
        else:
            col_sw, col_content = st.columns([1, 13])
            with col_sw: st.checkbox("Validar", key=chk_key, on_change=alternar_validacao, args=(idx_b,), label_visibility="collapsed")
            with col_content:
                col_b, col_m, col_l = st.columns([4, 3, 5])
                with col_b:
                    st.markdown(f"🗓️ **Data/Hora:** {b.get('dataEHora', '---')}")
                    st.markdown(f"👤 **Origem:** {b.get('origemDestinatario', '---')}")
                    st.markdown(f"💰 **Valor Banco:** `R$ {b.get('valor', 0):,.2f}`")
                with col_m:
                    st.success(f"🤖 **Match {item['metodo']}:** Linha(s) **{texto_linhas}**")
                    if item["metodo"] == "Manual": st.button("Desfazer Vínculo", key=f"btn_unl_{idx_b}", on_click=desfazer_vinculo_seguro, args=(idx_b,))
                with col_l:
                    for p in item["passagens"]:
                        s = p["dados"]
                        with st.container(border=True):
                            st.markdown(f"📋 **Linha Excel: {p['linha_excel']}** | Bilhete: {s.get('Num Passagem', '---')}")
                            st.markdown(f"💵 **Valor:** R$ {s.get('Valor', '0,00')} | **Pag:** {obter_pagador(s)}")
                            
        st.markdown("<hr style='margin: 0.4em 0px; border-color: #E2E8F0;'>", unsafe_allow_html=True)
        
    # 🔴 2. PIX NO BANCO SEM PASSAGEM
    if grupo_erros_banco:
        st.markdown("### 🔴 Pix Recebidos no Banco Sem Passagem Vinculada")
        sys_erros_cache = [{"idx_s": s["idx_s"], "linha_excel": s["linha_excel"], "dt_parsed": s["dt_parsed"], "valor_clean": s["valor_clean"], "label_base": f"Linha {s['linha_excel']} | Bilt: {s['dados'].get('Num Passagem','---')} | R$ {s['dados'].get('Valor','0.00')} | Pas: {obter_passageiro(s['dados'])}"} for s in grupo_erros_sistema]
            
    for b_item in grupo_erros_banco:
        idx_b, b, b_dt, b_val = b_item["idx_b"], b_item["banco"], b_item["dt_parsed"], float(b_item["banco"].get('valor', 0))
        col_b, col_m, col_l = st.columns([4, 3, 5])
        with col_b:
            st.markdown(f"🗓️ **Data/Hora:** {b.get('dataEHora', '---')}")
            st.markdown(f"👤 **Origem:** {b.get('origemDestinatario', '---')}")
            st.markdown(f"💰 **Valor Banco:** `R$ {b_val:,.2f}`")
        with col_m:
            st.error("❌ **PIX ÓRFÃO:** Sem correspondência.")
            existe_match_perfeito_valor = False
            if pd.notna(b_dt):
                for s in sys_erros_cache:
                    if pd.notna(s["dt_parsed"]) and (abs((b_dt - s["dt_parsed"]).total_seconds()) <= 60 or abs(abs((b_dt - s["dt_parsed"]).total_seconds()) - 3600) <= 60) and abs(b_val - s["valor_clean"]) < 0.01:
                        existe_match_perfeito_valor = True
                        break
            
            opcoes_selecao = []
            for s in sys_erros_cache:
                sugestao_prioridade = 0 
                rotulo_prefixo = ""
                if pd.notna(b_dt) and pd.notna(s["dt_parsed"]) and (abs((b_dt - s["dt_parsed"]).total_seconds()) <= 60 or abs(abs((b_dt - s["dt_parsed"]).total_seconds()) - 3600) <= 60):
                    if abs(b_val - s["valor_clean"]) < 0.01: sugestao_prioridade, rotulo_prefixo = 2, "🎯 [VALOR E HORA] "
                    elif not existe_match_perfeito_valor: sugestao_prioridade, rotulo_prefixo = 1, "💡 [HORA APROX] "
                opcoes_selecao.append({"idx_s": s["idx_s"], "label": rotulo_prefixo + s["label_base"], "prioridade": sugestao_prioridade})
                
            opcoes_selecao = sorted(opcoes_selecao, key=lambda x: x["prioridade"], reverse=True)
            ids_ordenados = [s["idx_s"] for s in opcoes_selecao]
            mapa_rotulos = {s["idx_s"]: s["label"] for s in opcoes_selecao}
            
            if ids_ordenados:
                st.multiselect("Vincular manual:", options=ids_ordenados, format_func=lambda x: mapa_rotulos.get(x, str(x)), key=f"ms_link_{idx_b}")
                st.button("Confirmar Vínculo Manual", key=f"btn_lnk_{idx_b}", on_click=confirmar_vinculo_seguro, args=(idx_b,))
            else: st.caption("Nenhuma passagem livre.")
        with col_l: st.write("---")
        st.markdown("<hr style='margin: 0.4em 0px; border-color: #F87171;'>", unsafe_allow_html=True)
        
    # ⚠️ 3. PASSAGENS PENDENTES
    if grupo_erros_sistema: st.markdown("### ⚠️ Passagens Pendentes no Sistema (Sem Pix)")
    for s_item in grupo_erros_sistema:
        col_b, col_m, col_l = st.columns([4, 3, 5])
        s = s_item["dados"]
        with col_b: st.write("---")
        with col_m:
            if pd.isna(s.get('Nsu')) or pd.isna(s.get('Autorizacao')): st.error(f"⚠️ **DADOS INCOMPLETOS (Linha {s_item['linha_excel']}):** Sem NSU/Aut.")
            else: st.error(f"❌ **PASSAGEM SEM PIX (Linha {s_item['linha_excel']}):** Sem registro no banco.")
        with col_l:
            with st.container(border=True):
                st.markdown(f"📋 **Linha Excel: {s_item['linha_excel']}** | Bilhete: {s.get('Num Passagem', '---')}")
                st.markdown(f"💵 **Valor:** R$ {s.get('Valor', '0,00')} | **Passageiro:** {obter_passageiro(s)}")
        st.markdown("<hr style='margin: 0.4em 0px; border-color: #FBBF24;'>", unsafe_allow_html=True)

    # --- 📄 EXPORTAÇÃO PDF ---
    st.markdown("### 🖨️ Fechamento e Emissão de Relatório")
    if st.button("📄 Gerar e Baixar Relatório em PDF"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", style="B", size=16)
        pdf.set_text_color(30, 41, 59) 
        pdf.cell(0, 10, txt="RELATORIO DE CONCILIACAO DE PIX", ln=1, align="C")
        pdf.set_font("Helvetica", size=10)
        pdf.set_text_color(100, 116, 139) 
        pdf.cell(0, 6, txt="Auditoria Automatizada, Vinculos Manuais e Validacao de Caixa", ln=1, align="C")
        pdf.ln(6) 
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 8, txt="1. Resumo Consolidado da Auditoria", ln=1)
        pdf.set_font("Helvetica", size=10)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(0, 6, txt=f" -> Total de Lancamentos Conciliados (Sucesso): {len(grupo_conciliados)}", ln=1)
        pdf.cell(0, 6, txt=f" -> Confirmados/Validados Manualmente por Voce: {len(st.session_state.validados)}", ln=1)
        pdf.cell(0, 6, txt=f" -> Alertas: Pix no Banco Sem Passagem Vinculada: {len(grupo_erros_banco)}", ln=1)
        pdf.cell(0, 6, txt=f" -> Alertas: Passagens no Sistema Pendentes de Recebimento: {len(grupo_erros_sistema)}", ln=1)
        pdf.ln(8) 
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.set_text_color(21, 128, 61) 
        pdf.cell(0, 8, txt="2. Detalhamento dos Lancamentos Conciliados", ln=1)
        pdf.ln(2)
        
        for item in grupo_conciliados:
            b = item["banco"]
            status_val = "VALIDADO" if item["idx_b"] in st.session_state.validados else "PENDENTE"
            pdf.set_draw_color(226, 232, 240)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(2) 
            pdf.set_font("Helvetica", style="B", size=9.5)
            pdf.set_text_color(15, 23, 42)
            pdf.cell(0, 5, txt=limpar_acentos(f"BANCO: {b.get('dataEHora')} | R$ {b.get('valor')} | Origem: {b.get('origemDestinatario')} [{status_val}]"), ln=1)
            pdf.set_font("Helvetica", size=8.5)
            pdf.set_text_color(71, 85, 105)
            for p in item["passagens"]:
                s = p["dados"]
                pdf.cell(0, 4.5, txt=limpar_acentos(f"    [Ticket] Linha {p['linha_excel']} | Bilhete: {s.get('Num Passagem')} | R$ {s.get('Valor')} | Pas: {obter_passageiro(s)}"), ln=1)
            pdf.ln(3) 
            
        pdf.ln(6) 
        if grupo_erros_banco:
            pdf.set_font("Helvetica", style="B", size=12)
            pdf.set_text_color(185, 28, 28) 
            pdf.cell(0, 8, txt="3. Alertas: Pix Recebidos no Banco Sem Passagem Vinculada", ln=1)
            pdf.ln(2)
            for b_item in grupo_erros_banco:
                b = b_item["banco"]
                pdf.set_draw_color(254, 202, 202) 
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(2)
                pdf.set_font("Helvetica", style="B", size=9)
                pdf.set_text_color(15, 23, 42)
                pdf.cell(0, 5, txt=limpar_acentos(f"BANCO (ORFAO): {b.get('dataEHora')} | R$ {b.get('valor')} | Origem: {b.get('origemDestinatario')}"), ln=1)
                pdf.ln(3) 
            pdf.ln(6)
            
        if grupo_erros_sistema:
            pdf.set_font("Helvetica", style="B", size=12)
            pdf.set_text_color(180, 83, 9) 
            pdf.cell(0, 8, txt="4. Alertas: Passagens no Sistema Sem Confirmacao de Pix", ln=1)
            pdf.ln(2)
            for s_item in grupo_erros_sistema:
                s = s_item["dados"]
                pdf.set_draw_color(253, 230, 138) 
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(2)
                pdf.set_font("Helvetica", style="B", size=9)
                pdf.set_text_color(15, 23, 42)
                pdf.cell(0, 5, txt=limpar_acentos(f"SISTEMA (ORFAO): Linha Excel {s_item['linha_excel']} | Bilhete: {s.get('Num Passagem')} | R$ {s.get('Valor')} | Pas: {obter_passageiro(s)}"), ln=1)
                pdf.ln(3) 
                
        st.download_button(label="📥 Clique aqui para Salvar o Arquivo PDF", data=bytes(pdf.output()), file_name="Relatorio_Conciliacao_Pix.pdf", mime="application/pdf")
else:
    if file_sistema and file_banco: st.info("👆 Clique em **INICIAR CONCILIAÇÃO** para cruzar os dados.")
    else: st.warning("Aguardando os dois arquivos para liberar a conciliação.")
