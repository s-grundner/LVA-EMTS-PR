import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class ADC:
    n_levels: int
    codes: np.ndarray

    INL_COLOR = 'FF728A'
    DNL_COLOR = 'FFEC21'
    NULL_COLOR = '8FFF5B'
    POS_END_COLOR = 'FF8438'
    NEG_END_COLOR = '35CCFF'

    def __init__(self, name, u_edge_meas, u_fsr=5, resolution=4, type='bipolar'):
        self.name = name
        self.u_fsr = u_fsr
        self.resolution = resolution
        self.n_levels = 2 ** resolution
        self.type = type
        self.u_edge_meas = u_edge_meas.to_numpy()
        match type:
            case 'unipolar':
                self.codes = np.arange(0, self.n_levels)
            case _:
                self.codes = np.arange(-self.n_levels//2, self.n_levels//2)
        
    def ideal(self):
        # Stufenmittelpunkte
        match self.type:
            case 'unipolar':
                u_mid = np.arange(0, self.u_fsr, self.u_fsr / self.n_levels)
            case _:
                u_mid = np.arange(-self.u_fsr/2, self.u_fsr/2, self.u_fsr / self.n_levels)
        
        # Stufenbreite
        u_width = np.ones(self.n_levels) * self.u_fsr / self.n_levels
        # Umschaltspunkte
        u_edge = u_mid + u_width / 2

        return pd.DataFrame({
            'Code': self.codes,
            'U_edge': u_edge,
            'U_width': u_width,
            'U_mid': u_mid           
        })
    
    def eval(self):
        df_ideal = self.ideal()
        u_edge_ideal = df_ideal['U_edge'].to_numpy()
        u_width_ideal = df_ideal['U_width'].to_numpy()
        u_mid_ideal = df_ideal['U_mid'].to_numpy()

        u_edge_diff = abs(self.u_edge_meas - u_edge_ideal[:-1])
        n = self.n_levels

        pos_end = u_edge_diff[0]
        neg_end = u_edge_diff[-2]
        null_pt = u_edge_diff[n//2]

        # Calc Correcting Factor
        i = np.arange(0, n-1)
        u_edge_korr = self.u_edge_meas[:n-1] - (neg_end*i + pos_end*(n-2-i))/(n-2)
        
        u_width_real = np.diff(u_edge_korr)
        u_mid_real = u_edge_korr[:-1] + u_width_real / 2

        u_width_diff = np.abs(u_width_real - u_width_ideal[1:-1])
        u_mid_diff = np.abs(u_mid_real - u_mid_ideal[1:-1])

        dnl = u_width_diff.max()
        inl = u_mid_diff.max()
        dnl_idx = np.argmax(u_width_diff) + 1
        inl_idx = np.argmax(u_mid_diff) + 1
        
        # Pack
        errors = {
            'pos_end': {'val' : pos_end, 'idx': 0},
            'neg_end': {'val' : neg_end, 'idx': n-2},
            'null_pt': {'val' : null_pt, 'idx': n//2},
            'dnl': {'val' : dnl, 'idx': dnl_idx},
            'inl': {'val' : inl, 'idx': inl_idx}
        }

        df_codes = pd.DataFrame({ 'Code': self.codes })
        df = pd.merge(pd.DataFrame({
            'Code': self.codes[:-1],
            'U_edge_real': self.u_edge_meas,
            'U_edge_ideal': df_ideal['U_edge'][:-1],
            'U_edge_diff': u_edge_diff
        }), pd.DataFrame({
            'Code': self.codes[1:-1],
            'U_width_real': u_width_real,
            'U_width_ideal': df_ideal['U_width'][1:-1],
            'U_width_diff': u_width_diff,
            'U_mittel_real': u_mid_real,
            'U_mittel_ideal': df_ideal['U_mid'][1:-1],
            'U_mittel_diff': u_mid_diff
        }), how='left', on='Code')

        # merge dataframes on code
        df = pd.merge(df_codes, df, how='left', on='Code')
        return (df, errors)
    
    def __curve(self):
        plt.step(self.ideal()['U_edge'], self.codes, where='pre')
        plt.step(self.u_edge_meas, self.codes[:-1], where='pre')
        plt.title(f'Umsetzerkennlinie: {self.name}')
        plt.xlabel('Eingangsspannung / V')
        plt.ylabel('Ausgangscode')
        plt.yticks(self.codes)
        plt.grid(True)
        plt.legend(['Ideal', 'Gemessen'])

    def plot_curve(self):
        self.__curve()
        plt.show()

    def save_curve(self, filename):
        self.__curve()
        plt.savefig(filename)
        plt.close()

    def __cell_color(self, col):
        return f'cellcolor:[HTML]{{{col}}}--wrap;'

    def to_latex(self, dir: str = 'latex/tables'):
        df_meas, errors = self.eval()
        
        def highlight_errors(s):
            props = pd.Series('', index=s.index)

            if s.name == 'U_edge_diff':
                props.iloc[errors['pos_end']['idx']] = self.__cell_color(self.POS_END_COLOR)
                props.iloc[errors['neg_end']['idx']] = self.__cell_color(self.NEG_END_COLOR)
                props.iloc[errors['null_pt']['idx']] = self.__cell_color(self.NULL_COLOR)
            elif s.name == 'U_width_diff':
                props.iloc[errors['dnl']['idx']] = self.__cell_color(self.DNL_COLOR)
            elif s.name == 'U_mittel_diff':
                props.iloc[errors['inl']['idx']] = self.__cell_color(self.INL_COLOR)
            return props


        rename_map = {
            'U_edge_real':  r'$U^\mathrm{real}_{\mathrm{edge}}$',
            'U_edge_ideal': r'$U^\mathrm{ideal}_{\mathrm{edge}}$',
            'U_edge_diff':  r'$\Delta U_{\mathrm{edge}}$',
            'U_width_real': r'$U^\mathrm{real}_{\mathrm{width}}$',
            'U_width_diff': r'$\Delta U_{\mathrm{width}}$',
            'U_width_ideal': r'$U^\mathrm{ideal}_{\mathrm{width}}$',
            'U_mittel_diff': r'$\Delta U_{\mathrm{mid}}$',
            'U_mittel_real': r'$U^\mathrm{real}_{\mathrm{mid}}$',
            'U_mittel_ideal': r'$U^\mathrm{ideal}_{\mathrm{mid}}$'
        }

        sty = df_meas.style\
            .format(precision=3,na_rep='-')\
            .hide(level=0, axis=0)\
            .apply(highlight_errors)\
            .set_table_styles([ {'selector': 'midrule', 'props': ':midrule;'} ])\
            .format_index(rename_map.get, axis=1)

        filename_meas = self.name.lower().replace(" ", "_") + '_table.tex'
        buf = f'{dir}/{filename_meas}'

        sty.to_latex(
            buf=buf,
            caption=f'ADC Auswertung: {self.name}',
            label=f'tab:{self.name.lower().replace(" ", "_")}',
            position='htbp',
            environment='table',
            position_float='centering',
            column_format='c|ccc|ccc|ccc',
        )


    def err_to_latex(self, dir: str = 'latex/tables'):
        df, errors = self.eval()
        rows = []
        for key, err in errors.items():
            rows.append({
                'Fehler': key,
                'Wert': err['val'],
                'Code': df['Code'][err['idx']]
            })
        df_err = pd.DataFrame(rows)

        def rename_err(col):
            match col:
                case 'pos_end': return f'{{\\cellcolor[HTML]{{{self.POS_END_COLOR}}} Positiver Endwertfehler}}'
                case 'neg_end': return f'{{\\cellcolor[HTML]{{{self.NEG_END_COLOR}}} Negativer Endwertfehler}}'
                case 'null_pt': return f'{{\\cellcolor[HTML]{{{self.NULL_COLOR}}} Nullpunktfehler}}'
                case 'dnl': return f'{{\\cellcolor[HTML]{{{self.DNL_COLOR}}} Differentielle Nichtlinearität}}'
                case 'inl': return f'{{\\cellcolor[HTML]{{{self.INL_COLOR}}} Integrale Nichtlinearität}}'
                case _: return col

        sty = df_err.style\
            .format({'Fehler': lambda c: rename_err(c)}, precision=3, na_rep='-')\
            .hide(level=0, axis=0)\
            .set_table_styles([ {'selector': 'midrule', 'props': ':midrule;'} ])\
        
        filename_err = self.name.lower().replace(" ", "_") + '_errors.tex'
        buf = f'{dir}/{filename_err}'
        sty.to_latex(
            buf=buf,
            caption=f'ADC Fehlerwerte: {self.name}',
            label=f'tab:{self.name.lower().replace(" ", "_")}_errors',
            position='htbp',    
            environment='table',
            position_float='centering',
            column_format='ccc',
            encoding='utf-8'
        )
