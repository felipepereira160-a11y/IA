import pandas as pd
from haversine import haversine, Unit

def suggest_rt_for_city(df_map, city_name,
                        city_lat_col='cd_latitude_atendimento', city_lon_col='cd_longitude_atendimento',
                        rep_col='nm_representante', rep_lat_col='cd_latitude_representante', rep_lon_col='cd_longitude_representante',
                        exclude_terms=None):
    if exclude_terms is None:
        exclude_terms = ['stellantis', 'ceabs', 'fca chrysler']
    # Get city point
    city_rows = df_map[df_map['nm_cidade_atendimento'] == city_name]
    if city_rows.empty:
        raise ValueError(f"Coordenadas para '{city_name}' não encontradas no Mapeamento.")
    ponto = (city_rows.iloc[0][city_lat_col], city_rows.iloc[0][city_lon_col])
    distancias = []
    df_map_filtered = df_map.copy()
    if rep_col in df_map_filtered.columns:
        mask = ~df_map_filtered[rep_col].astype(str).str.lower().str.contains('|'.join(exclude_terms))
        df_map_filtered = df_map_filtered[mask]
    for _, row in df_map_filtered.iterrows():
        try:
            d = haversine((row[rep_lat_col], row[rep_lon_col]), ponto, unit=Unit.KILOMETERS)
            distancias.append({'Representante': row[rep_col], 'Distancia (km)': d})
        except Exception:
            continue
    return pd.DataFrame(distancias).drop_duplicates(subset=['Representante']).reset_index(drop=True)
