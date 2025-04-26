# Aplicação Streamlit para Visualização do Modelo e Análise Exploratória

import streamlit as st
import pandas as pd
import numpy as np
import os
import joblib 
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor # Apenas para type hint
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
# Importar display opcionalmente para tabelas no Colab (não usado no Streamlit direto)
# from IPython.display import display

# --- Configurações Iniciais ---
st.set_page_config(layout="wide", page_title="Dashboard Produtividade Milho")

st.title("🌽 Dashboard de Produtividade de Milho (Sorriso-MT)")
st.markdown("Análise Exploratória dos Dados e Avaliação do Modelo Preditivo (RandomForest por Safra).")

# --- Definição Global de Caminhos ---
processed_folder = 'dados_processados'
results_folder = 'resultados'
model_folder = os.path.join(results_folder, 'modelos')
consolidated_monthly_path = os.path.join(processed_folder, 'base_consolidada_mensal.csv')
milho_path = os.path.join(processed_folder, 'milho.csv')
# Ajuste o nome do modelo se salvou com outro nome na Etapa 3
model_path = os.path.join(model_folder, 'modelo_final_rf_por_safra_otimizado.joblib')

# --- Funções Auxiliares (Cache para Performance) ---

@st.cache_data # Cache para dados carregados
def carregar_dados_base(monthly_path, milho_path_func):
    """Carrega e faz uma preparação mínima nos DataFrames base."""
    df_mensal = None
    df_milho_proc = None
    erro_carga = False

    if not os.path.exists(monthly_path): st.error(f"Erro: Arquivo não encontrado: {monthly_path}"); erro_carga = True
    if not os.path.exists(milho_path_func): st.error(f"Erro: Arquivo não encontrado: {milho_path_func}"); erro_carga = True
    if erro_carga: return None, None

    try:
        df_mensal = pd.read_csv(monthly_path)
        df_milho_proc = pd.read_csv(milho_path_func)

        # Preparação mínima (tipos de dados chave)
        if 'ANO' in df_mensal.columns: df_mensal['ANO'] = pd.to_numeric(df_mensal['ANO'], errors='coerce').astype('Int64')
        else: raise ValueError("Coluna 'ANO' ausente em df_mensal.")
        if 'MES' in df_mensal.columns: df_mensal['MES'] = pd.to_numeric(df_mensal['MES'], errors='coerce').astype('Int64')
        else: raise ValueError("Coluna 'MES' ausente em df_mensal.")
        df_mensal.dropna(subset=['ANO', 'MES'], inplace=True)
        # Cria coluna DATA se não existir, para plots temporais
        if 'DATA_MES' not in df_mensal.columns:
             df_mensal['DATA_MES'] = pd.to_datetime(df_mensal['ANO'].astype(str) + '-' + df_mensal['MES'].astype(str) + '-01', errors='coerce')

        if 'ANO' in df_milho_proc.columns: df_milho_proc['ANO'] = pd.to_numeric(df_milho_proc['ANO'], errors='coerce').astype('Int64')
        else: raise ValueError("Coluna 'ANO' ausente em df_milho_proc.")
        if 'Produtividade_Anual' in df_milho_proc.columns: df_milho_proc['Produtividade_Anual'] = pd.to_numeric(df_milho_proc['Produtividade_Anual'], errors='coerce')
        else: raise ValueError("Coluna 'Produtividade_Anual' ausente em df_milho_proc.")
        if 'safra' not in df_milho_proc.columns: raise ValueError("Coluna 'safra' ausente em df_milho_proc.")
        df_milho_proc.dropna(subset=['ANO', 'Produtividade_Anual', 'safra'], inplace=True)

        return df_mensal, df_milho_proc

    except Exception as e:
        st.error(f"Erro ao carregar ou preparar dados base: {e}")
        return None, None

@st.cache_data
def agregar_features_por_safra(_df_mensal, _df_milho_proc):
    """Agrega features climáticas/NDVI por safra."""
    # (Lógica de agregação idêntica à da Etapa 3)
    if _df_mensal is None or _df_milho_proc is None: return None
    meses_safra1 = [(10, -1), (11, -1), (12, -1), (1, 0), (2, 0)]
    meses_safra2 = [(2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)]
    meses_safra3 = [(5, 0), (6, 0), (7, 0), (8, 0), (9, 0)]
    agg_config = {
        'mean': ['RADIACAO_media_mensal', 'TEMPERATURA_media_mensal', 'UMIDADE_media_mensal', 'VENTO_VEL_media_mensal', 'NDVI_satveg_mensal'],
        'min':  ['RADIACAO_media_mensal', 'TEMPERATURA_media_mensal', 'UMIDADE_media_mensal', 'NDVI_satveg_mensal'],
        'max':  ['RADIACAO_media_mensal', 'TEMPERATURA_media_mensal', 'UMIDADE_media_mensal', 'VENTO_VEL_media_mensal', 'NDVI_satveg_mensal'],
        'sum':  ['PRECIPITACAO_mm_mensal_soma']
    }
    lista_features_safra = []
    for index, row in _df_milho_proc.iterrows():
        ano_agricola = row['ANO']; tipo_safra = row['safra']; produtividade = row['Produtividade_Anual']
        meses_anos_target = []; meses_anos_base = None
        if '1ª' in tipo_safra: meses_anos_base = meses_safra1
        elif '2ª' in tipo_safra: meses_anos_base = meses_safra2
        elif '3ª' in tipo_safra: meses_anos_base = meses_safra3
        else: continue
        for mes, deslocamento_ano in meses_anos_base: meses_anos_target.append((ano_agricola + deslocamento_ano, mes))
        df_mensal_safra = _df_mensal[_df_mensal.set_index(['ANO', 'MES']).index.isin(meses_anos_target)]
        if df_mensal_safra.empty: continue
        features_safra_dict = {'ANO': ano_agricola, 'safra': tipo_safra, 'Produtividade_Anual': produtividade}
        for agg_func, cols_to_agg in agg_config.items():
            cols_existentes = [col for col in cols_to_agg if col in df_mensal_safra.columns]
            if not cols_existentes: continue
            try:
                aggregated_data = df_mensal_safra[cols_existentes].agg(agg_func)
                for col_original, valor_agregado in aggregated_data.items(): features_safra_dict[f"{col_original}_{agg_func}_safra"] = valor_agregado
            except Exception as e_agg: print(f"Erro agregando {agg_func} para {ano_agricola}/{tipo_safra}: {e_agg}")
        lista_features_safra.append(features_safra_dict)
    if lista_features_safra:
        df_modelar_safra = pd.DataFrame(lista_features_safra)
        if 'ANO' in df_modelar_safra.columns and 'safra' in df_modelar_safra.columns:
            df_modelar_safra = df_modelar_safra.set_index(['ANO', 'safra']).sort_index()
            return df_modelar_safra
    return None

@st.cache_data
def preparar_X_y(_df_modelar_safra):
    """Prepara X e y a partir do DataFrame agregado por safra."""
    # (Lógica idêntica à da Etapa 3)
    if _df_modelar_safra is None or 'Produtividade_Anual' not in _df_modelar_safra.columns: return None, None, None
    target = 'Produtividade_Anual'; y = _df_modelar_safra[target]
    features_cols_init = [col for col in _df_modelar_safra.columns if col != target]
    X = _df_modelar_safra[features_cols_init].copy()
    X['ANO_f'] = X.index.get_level_values('ANO').astype(int)
    X['safra_f'] = X.index.get_level_values('safra')
    X = pd.get_dummies(X, columns=['safra_f'], prefix='safra', drop_first=True)
    features_cols = X.columns.tolist()
    if X.isnull().any().any():
         st.warning("Preenchendo NaNs nas features com a média...")
         numeric_cols = X.select_dtypes(include=np.number).columns
         means = X[numeric_cols].mean(); means = means.fillna(0)
         X.fillna(means, inplace=True)
         if X.isnull().any().any(): st.error(f"NaNs persistentes: {X.columns[X.isnull().any()].tolist()}."); return None, None, None
    return X, y, features_cols

@st.cache_resource # Cache para o modelo carregado
def carregar_modelo(model_path_func):
    """Carrega o modelo .joblib salvo."""
    if not os.path.exists(model_path_func):
        st.error(f"Erro: Arquivo do modelo não encontrado em '{model_path_func}'. Execute a Etapa 3 para salvá-lo.")
        return None
    try:
        model = joblib.load(model_path_func)
        st.success(f"Modelo carregado com sucesso de: {model_path_func}")
        return model
    except Exception as e:
        st.error(f"Erro ao carregar o modelo: {e}")
        return None

# --- Carregamento e Preparação dos Dados ---
df_mensal, df_milho_proc = carregar_dados_base(consolidated_monthly_path, milho_path)
df_modelar_safra = agregar_features_por_safra(df_mensal, df_milho_proc)
X, y, features_cols = preparar_X_y(df_modelar_safra)
best_model_rf = carregar_modelo(model_path)

# --- Criação das Abas ---
tab1, tab2 = st.tabs(["📊 Análise Exploratória", "🤖 Avaliação do Modelo"])

# --- Aba 1: Análise Exploratória ---
with tab1:
    st.header("Análise Exploratória dos Dados")

    if df_mensal is not None and df_milho_proc is not None:
        st.markdown("Visualização das tendências e padrões nos dados originais processados.")

        # Sub-abas para organizar a EDA
        sub_tab_clima, sub_tab_ndvi, sub_tab_prod, sub_tab_corr = st.tabs([
            "Clima", "NDVI (SatVeg)", "Produtividade", "Correlações"
        ])

        with sub_tab_clima:
            st.subheader("Séries Temporais Climáticas (Médias Mensais)")
            if 'DATA_MES' in df_mensal.columns:
                fig_clima, axes_clima = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
                plot_vars_clima = {
                    'TEMPERATURA_media_mensal': ('Temperatura (°C)', 'red', axes_clima[0]),
                    'RADIACAO_media_mensal': ('Radiação (W/m² ?)', 'orange', axes_clima[1]),
                    'PRECIPITACAO_mm_mensal_soma': ('Precipitação (mm/mês)', 'blue', axes_clima[2]),
                    'UMIDADE_media_mensal': ('Umidade Relativa (%)', 'green', axes_clima[3])
                    # Adicionar Vento se desejar
                }
                plot_count_clima = 0
                for col, (label, color, ax) in plot_vars_clima.items():
                    if col in df_mensal.columns and not df_mensal[col].isnull().all():
                        ax.plot(df_mensal['DATA_MES'], df_mensal[col], label=label.split('(')[0].strip(), color=color, alpha=0.8)
                        ax.set_ylabel(label)
                        ax.grid(True, alpha=0.5); ax.legend(loc='upper left')
                        plot_count_clima += 1

                if plot_count_clima > 0:
                    axes_clima[-1].set_xlabel('Data')
                    plt.suptitle("Evolução Mensal das Variáveis Climáticas", y=1.02)
                    plt.tight_layout(rect=[0, 0.03, 1, 0.98])
                    st.pyplot(fig_clima)
                else:
                    st.warning("Não foi possível gerar gráficos climáticos (dados ausentes).")
            else:
                 st.warning("Coluna 'DATA_MES' não encontrada para plots climáticos.")

        with sub_tab_ndvi:
            st.subheader("NDVI SatVeg (Médio Mensal)")
            if 'DATA_MES' in df_mensal.columns and 'NDVI_satveg_mensal' in df_mensal.columns:
                # Série Temporal NDVI
                fig_ndvi_ts, ax_ndvi_ts = plt.subplots(figsize=(12, 4))
                ax_ndvi_ts.plot(df_mensal['DATA_MES'], df_mensal['NDVI_satveg_mensal'], marker='.', linestyle='-', label='NDVI SatVeg Médio Mensal')
                ax_ndvi_ts.set_title('Série Temporal NDVI Médio Mensal (SatVeg)')
                ax_ndvi_ts.set_xlabel('Data'); ax_ndvi_ts.set_ylabel('NDVI Médio Mensal')
                ax_ndvi_ts.grid(True, alpha=0.5); ax_ndvi_ts.legend()
                st.pyplot(fig_ndvi_ts)

                # Perfil Sazonal Médio
                if 'MES' in df_mensal.columns:
                     df_perfil_st = df_mensal.dropna(subset=['MES', 'NDVI_satveg_mensal'])
                     if not df_perfil_st.empty:
                          perfil_ndvi = df_perfil_st.groupby('MES').agg(NDVI_medio=('NDVI_satveg_mensal', 'mean'), NDVI_std=('NDVI_satveg_mensal', 'std'))
                          if not perfil_ndvi.empty:
                               fig_ndvi_saz, ax_ndvi_saz = plt.subplots(figsize=(10, 5))
                               ax_ndvi_saz.errorbar(perfil_ndvi.index, perfil_ndvi['NDVI_medio'], yerr=perfil_ndvi['NDVI_std'], label='NDVI SatVeg Médio ± Desv Padrão', fmt='-o', capsize=5)
                               ax_ndvi_saz.set_title('Perfil Sazonal Médio do NDVI SatVeg')
                               ax_ndvi_saz.set_xlabel('Mês do Ano'); ax_ndvi_saz.set_ylabel('Valor Médio NDVI')
                               ax_ndvi_saz.set_xticks(range(1, 13)); ax_ndvi_saz.legend(); ax_ndvi_saz.grid(True)
                               st.pyplot(fig_ndvi_saz)
                          else: st.warning("Não foi possível calcular o perfil sazonal do NDVI.")
                     else: st.warning("Não há dados válidos para o perfil sazonal do NDVI.")
                else: st.warning("Coluna 'MES' não encontrada para perfil sazonal.")
            else:
                 st.warning("Colunas 'DATA_MES' ou 'NDVI_satveg_mensal' não encontradas.")

        with sub_tab_prod:
            st.subheader("Produtividade de Milho (CONAB - MT)")
            colunas_num_prod = ['area_plantada_mil_ha', 'producao_mil_t', 'Produtividade_Anual']
            colunas_num_prod_ok = [c for c in colunas_num_prod if c in df_milho_proc.columns]

            if 'ANO' in df_milho_proc.columns and 'safra' in df_milho_proc.columns and colunas_num_prod_ok:
                 # Evolução por Safra
                 st.write("Evolução por Safra:")
                 for coluna in colunas_num_prod_ok:
                      fig_prod_ts, ax_prod_ts = plt.subplots(figsize=(12, 4))
                      sns.lineplot(data=df_milho_proc, x='ANO', y=coluna, hue='safra', marker='o', errorbar=None, ax=ax_prod_ts)
                      ax_prod_ts.set_title(f'Evolução - {coluna} por Safra')
                      ax_prod_ts.set_xlabel('Ano'); ax_prod_ts.set_ylabel(coluna.replace('_', ' ').title())
                      ax_prod_ts.legend(title='Safra'); ax_prod_ts.grid(True)
                      st.pyplot(fig_prod_ts)

                 # Boxplot Produtividade por Ano e Safra
                 st.write("Distribuição da Produtividade por Ano e Safra:")
                 df_milho_proc['ANO'] = pd.to_numeric(df_milho_proc['ANO'], errors='coerce')
                 df_milho_proc_plot = df_milho_proc.dropna(subset=['ANO', 'Produtividade_Anual', 'safra'])
                 if not df_milho_proc_plot.empty:
                      fig_prod_box, ax_prod_box = plt.subplots(figsize=(14, 7))
                      sns.boxplot(x='ANO', y='Produtividade_Anual', hue='safra', data=df_milho_proc_plot, ax=ax_prod_box)
                      ax_prod_box.set_title('Distribuição da Produtividade Anual por Ano e Safra')
                      ax_prod_box.set_xlabel('Ano'); ax_prod_box.set_ylabel('Produtividade (t/ha)')
                      ax_prod_box.tick_params(axis='x', rotation=45)
                      ax_prod_box.grid(True, axis='y')
                      ax_prod_box.legend(title='Safra', bbox_to_anchor=(1.05, 1), loc='upper left')
                      plt.tight_layout(rect=[0, 0, 0.9, 1])
                      st.pyplot(fig_prod_box)
                 else: st.warning("Não há dados válidos para gerar boxplot de produtividade.")
            else:
                 st.warning("Colunas necessárias para gráficos de produtividade não encontradas.")

        with sub_tab_corr:
            st.subheader("Matriz de Correlação (Base Mensal)")
            st.markdown("Mostra a correlação linear entre as médias/somas mensais e a produtividade anual (repetida).")
            colunas_corr_prod = [
                'RADIACAO_media_mensal', 'TEMPERATURA_media_mensal', 'PRECIPITACAO_mm_mensal_soma',
                'UMIDADE_media_mensal', 'VENTO_VEL_media_mensal', 'NDVI_satveg_mensal',
                'Produtividade_Anual'
            ]
            colunas_corr_existentes = [col for col in colunas_corr_prod if col in df_consolidado_mensal.columns]

            if len(colunas_corr_existentes) > 1:
                df_corr = df_consolidado_mensal[colunas_corr_existentes].dropna()
                if not df_corr.empty and len(df_corr) > 1:
                     matriz_corr_final = df_corr.corr()
                     fig_corr, ax_corr = plt.subplots(figsize=(10, 8))
                     sns.heatmap(matriz_corr_final, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, ax=ax_corr)
                     ax_corr.set_title('Matriz de Correlação (Base Mensal, Incluindo Produtividade)')
                     st.pyplot(fig_corr)

                     if 'Produtividade_Anual' in matriz_corr_final.columns:
                          st.write("**Correlação com Produtividade_Anual:**")
                          st.dataframe(matriz_corr_final['Produtividade_Anual'].sort_values(ascending=False).to_frame())
                     else: st.warning("Coluna 'Produtividade_Anual' não encontrada na matriz.")
                else: st.warning("Não há dados suficientes após remover NaNs para calcular a matriz de correlação.")
            else: st.warning("Não há colunas suficientes ou válidas para calcular a matriz de correlação final.")

    else:
        st.error("Falha ao carregar os dados necessários para a Análise Exploratória.")


# --- Aba 2: Avaliação do Modelo ---
with tab2:
    st.header("Avaliação do Modelo Otimizado (RandomForest por Safra)")

    # Verifica se tudo carregou e foi preparado para o modelo
    if X is not None and y is not None and best_model_rf is not None:

        # Recriar a divisão Treino/Teste
        X_train, X_test, y_train, y_test = None, None, None, None
        try:
            safra_original = df_modelar_safra.loc[X.index].index.get_level_values('safra')
            test_size_ratio = 0.25
            min_samples_per_class = 2
            counts = safra_original.value_counts()
            y = y.loc[X.index] # Alinhamento

            if safra_original.nunique() > 1 and all(counts >= min_samples_per_class):
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size_ratio, random_state=42, stratify=safra_original)
            else:
                st.warning("Não foi possível estratificar. Usando divisão aleatória simples.")
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size_ratio, random_state=42)
            st.write(f"Dados divididos para avaliação: {len(X_train)} treino, {len(X_test)} teste.")

        except Exception as e_split:
             st.error(f"Erro ao recriar divisão treino/teste: {e_split}")

        # Avaliar no conjunto de teste
        if X_test is not None and y_test is not None:
            try:
                X_test = X_test.reindex(columns=X_train.columns, fill_value=0) # Garante mesmas colunas
                y_pred = best_model_rf.predict(X_test)
                r2 = r2_score(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                mae = mean_absolute_error(y_test, y_pred)

                st.subheader("Métricas de Desempenho (Conjunto de Teste)")
                col1, col2, col3 = st.columns(3)
                col1.metric("R² (R-quadrado)", f"{r2:.4f}")
                col2.metric("RMSE (t/ha)", f"{rmse:.4f}")
                col3.metric("MAE (t/ha)", f"{mae:.4f}")
                st.caption(f"R²: Proporção da variância explicada. RMSE/MAE: Erro médio da previsão.")

                st.subheader("Gráficos de Avaliação do Modelo")
                col_g1, col_g2 = st.columns(2)

                with col_g1:
                    fig1, ax1 = plt.subplots(figsize=(6, 6))
                    ax1.scatter(y_test, y_pred, alpha=0.7, edgecolors='k', s=50)
                    min_val = min(y_test.min(), y_pred.min()) - 0.5; max_val = max(y_test.max(), y_pred.max()) + 0.5
                    ax1.plot([min_val, max_val], [min_val, max_val], '--r', linewidth=2, label='Ideal (y=x)')
                    ax1.set_xlabel('Produtividade Real (t/ha)'); ax1.set_ylabel('Produtividade Prevista (t/ha)')
                    ax1.set_title('Real vs. Previsto (Teste)'); ax1.legend(); ax1.grid(True); ax1.axis('equal'); ax1.set_xlim(min_val, max_val); ax1.set_ylim(min_val, max_val)
                    st.pyplot(fig1)

                with col_g2:
                    if hasattr(best_model_rf, 'feature_importances_') and hasattr(X_train, 'columns'):
                        importances = best_model_rf.feature_importances_
                        feature_names = X_train.columns
                        feature_importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
                        feature_importance_df = feature_importance_df.sort_values(by='Importance', ascending=False)
                        fig2, ax2 = plt.subplots(figsize=(6, 7))
                        sns.barplot(x='Importance', y='Feature', data=feature_importance_df.head(15), ax=ax2, palette='viridis')
                        ax2.set_title('Importância das Features (Modelo Otimizado)')
                        plt.tight_layout()
                        st.pyplot(fig2)
                    else: st.warning("Não foi possível extrair a importância das features.")

                if st.checkbox("Mostrar Tabela de Comparação Detalhada"):
                    st.subheader("Comparação Detalhada (Conjunto de Teste)")
                    df_resultados = pd.DataFrame({'Real': y_test, 'Previsto': y_pred}, index=y_test.index)
                    df_resultados['Erro'] = df_resultados['Real'] - df_resultados['Previsto']
                    df_resultados['Erro (%)'] = (df_resultados['Erro'] / df_resultados['Real']) * 100
                    st.dataframe(df_resultados.style.format({'Real': '{:.2f}', 'Previsto': '{:.2f}', 'Erro': '{:.2f}', 'Erro (%)': '{:.1f}%'}).background_gradient(cmap='RdYlGn_r', subset=['Erro'], axis=0, low=0.4, high=0.4))

            except Exception as e_eval: st.error(f"Erro ao avaliar o modelo no conjunto de teste: {e_eval}")
        else: st.error("Não foi possível recriar os dados de teste para avaliação.")
    else:
        st.error("Não foi possível carregar dados ou modelo para avaliação. Verifique as etapas anteriores e os caminhos.")

# --- Sidebar ---
st.sidebar.header("Sobre")
st.sidebar.info("Dashboard de previsão de produtividade de milho (Sorriso-MT) usando RandomForest, dados climáticos e NDVI SatVeg por safra.")
st.sidebar.header("Arquivos Necessários")
st.sidebar.markdown(f"- `{os.path.basename(consolidated_monthly_path)}`")
st.sidebar.markdown(f"- `{os.path.basename(milho_path)}`")
st.sidebar.markdown(f"- `{os.path.basename(model_path)}`")
# st.sidebar.markdown(f"*(Opcional: `{os.path.basename(solo_path)}`)*") # Comentado pois não usamos solo

