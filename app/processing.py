import pandas as pd
import datetime

class DojoAttendanceProcessor:
    def __init__(self, public_holidays=None):
        # Default public holidays, can be overridden
        self.public_holidays = public_holidays or {
            'Perú': [
                datetime.date(2024, 7, 28),
                datetime.date(2024, 7, 29),
            ],
            'Colombia': [
                datetime.date(2024, 8, 7),
                datetime.date(2024, 8, 15),
            ]
        }

    def get_last_week_workdays(self, country):
        today = datetime.date.today()
        last_monday = today - datetime.timedelta(days=today.weekday() + 7)
        last_friday = last_monday + datetime.timedelta(days=4)
        all_days = [last_monday + datetime.timedelta(days=i) for i in range(5)]
        holidays = self.public_holidays.get(country, [])
        workdays = [d for d in all_days if d not in holidays]
        return {
            'init_date': last_monday,
            'end_date': last_friday,
            'total_workdays': len(workdays)
        }

    def process(self, country, excel_file):
        # Read Excel sheets
        sheet_names = pd.ExcelFile(excel_file).sheet_names
        df_looker_tcbp = pd.read_excel(excel_file, sheet_name='Looker TCBP')
        df_eligible_Dojo = pd.read_excel(excel_file, sheet_name='Today elegible Dojo')
        df_eligible_Dojo['Puede asistir?'] = df_eligible_Dojo['Puede asistir?'].fillna('Si')

        dojo_total_number = df_eligible_Dojo[
            (df_eligible_Dojo['Country'] == country.upper()[:2]) & (df_eligible_Dojo['Puede asistir?'] == 'Si')
        ]

        # Filter dojo_total_number to only include rows where 'Fecha esperada 5 dias' < today
        today = datetime.date.today()
        fecha_esperada = pd.to_datetime(
            dojo_total_number['Fecha esperada 5 dias'], 
            format='%d/%m/%Y', 
            errors='coerce'
        )
        # Filter out NaT values and compare with today, format dates as YYYY-MM-DD
        mask = (~fecha_esperada.isna()) & (fecha_esperada.dt.date < today)
        dojo_total_number_filtered = dojo_total_number[mask].copy()
        dojo_total_number_filtered['Fecha esperada 5 dias'] = fecha_esperada[mask].dt.strftime('%Y-%m-%d')
        # print(dojo_total_number_filtered.shape)
        # print(dojo_total_number_filtered['Fecha esperada 5 dias'])
        # print(len(dojo_total_number['Fecha esperada 5 dias']))
        # print(dojo_total_number['Fecha esperada 5 dias'])

        result = self.get_last_week_workdays(country)

        # Processing logic
        cumplio = []
        Follow_up = []
        dias_str = ['5 dias', '4 dias', '3 dias', '2 dias', '1 dia']
        for i in range(dojo_total_number_filtered.shape[0]):
            days = dojo_total_number_filtered['Esquema de asistencia a la fecha'].iloc[i]
            if days in dias_str:
                dias_int = int(days.split()[0])
                if dojo_total_number_filtered['Last week attendance'].iloc[i] >= dias_int:
                    cumplio.append('Si')
                    Follow_up.append('No_aplica')
                else:
                    cumplio.append('No')
                    if dojo_total_number_filtered['Last week attendance'].iloc[i] > 2:
                        if dias_int == 5:
                            Follow_up.append(f'Le corresponde assistir {dias_int} pero fueron de 3 a 4 dias')
                        elif dias_int == 4:
                            Follow_up.append(f'Le corresponde assistir {dias_int} pero fueron de 3 dias')
                    else:
                        Follow_up.append(f'Le corresponde assistir {dias_int} pero fueron de 0 a 2 dias')
            else:
                cumplio.append('Si')
                Follow_up.append('No_aplica')

        temporal_df = dojo_total_number_filtered[['Work Email','Full Name','Current Skill','Current Seniority','Glober Studio','Project Name','Last Entry Date','Dojo start date','Percentage','Country','City', 'Last week attendance', 'Esquema de asistencia a la fecha']].copy()
        temporal_df['cumplio'] = cumplio
        temporal_df['Follow_up'] = Follow_up

        new_row = {
            'País': country,
            'Fecha de asistencia': result['init_date'],
            'Fecha de revisión ': datetime.date.today(),
            'Globers en DOJO': dojo_total_number.shape[0],
            'Globers que tienen que asistir': dojo_total_number_filtered.shape[0],   ### need to change by the total number of globers that have to attend according to the filters
            'Globers que cumplieron ': (temporal_df[temporal_df['cumplio'] == 'Si']).shape[0],
            'Revisión para seguimiento': None,
            '% de cumplimiento': (temporal_df[temporal_df['cumplio'] == 'Si']).shape[0] / dojo_total_number_filtered.shape[0] if dojo_total_number_filtered.shape[0] > 0 else 0,
            'Globers que incumplieron': (temporal_df[temporal_df['cumplio'] == 'No']).shape[0],
            'Sin justificación ': None,
            'Recordatorio de procedimiento': None,
            'Proceso disciplinario': None,
            '% de incumplimiento': None
        }

        df_looker_tcbp = pd.concat([df_looker_tcbp, pd.DataFrame([new_row])], ignore_index=True)

        report = temporal_df[temporal_df['cumplio'] == 'No'].copy()
        report_cleaned = report[['Follow_up', 'Work Email', 'Last week attendance', 'Esquema de asistencia a la fecha']].sort_values(by='Follow_up', ascending=True).reset_index(drop=True)

        return df_looker_tcbp, report_cleaned
