import numpy as np
import pandas as pd

class ADC:
    def __init__(self, u_fsr, resolution, type='unipolar'):
        self.u_fsr = u_fsr
        self.resolution = resolution
        self.n_levels = 2 ** resolution
        match type:
            case 'unipolar':
                self.codes = np.arange(0, n_levels)
            case _:
                self.codes = np.arange(-n_levels/2, n_levels/2)
        
    def ideal(self):
        # Stufenmittelpunkte
        match self.type:
            case 'unipolar':
                u_mid = np.arange(0, u_fsr, u_fsr / n_levels)
            case _:
                u_mid = np.arange(-u_fsr/2, +u_fsr/2, u_fsr / n_levels)
        
        # Stufenbreite
        u_width = np.ones(n_levels) * u_fsr / n_levels
        # Umschaltspunkte
        u_edge = u_mid + u_width / 2

        return pd.DataFrame({
            'Code': self.codes,
            'U_edge': u_edge,
            'U_width': u_width,
            'U_mid': u_mid           
        })
    
    def eval(self, u_edge_real):
        df_ideal = self.ideal()
        u_edge_diff = abs(u_edge_real - df_ideal['U_edge'][:-1])

        pos_end = u_edge_diff[-2]
        neg_end = u_edge_diff[0]
        null_pt = u_edge_diff[int(n_levels/2)]

        # Calc Correcting Factor
        n_vals = self.n_levels-2
        u_edge_korr = np.array([
            u_edge_real[i] - (neg_end*i + pos_end*(n_vals-i))/n_vals
            for i in range(n_vals+1)
        ])
        
        u_width_real = np.array([
            u_edge_korr[i+1] - u_edge_korr[i]
            for i in range(n_levels-2)
        ])
        u_mid_real = u_edge_korr[:-1] + u_width_real / 2

        u_width_diff = np.abs(u_width_real - df_ideal['U_width'][1:-1])
        u_mid_diff = np.abs(u_mid_real - df_ideal['U_mid'][1:-1])

        dnl = np.max(np.abs(u_width_diff))
        inl = np.max(np.abs(u_mid_diff))
        
        # Pack
        errors = {
            'pos_end': pos_end,
            'neg_end': neg_end,
            'null_pt': null_pt,
            'dnl': dnl,
            'inl': inl
        }
        df_errors = pd.DataFrame(data=errors, index=[''])

        df_codes = pd.DataFrame({ 'Code': self.codes })
        df = pd.merge(pd.DataFrame({
            'Code': self.codes[:-1],
            'U_edge_real': u_edge_real,
            'U_edge_ideal': df_ideal['U_edge'][:-1],
            'U_edge_diff': u_edge_diff
        }), pd.DataFrame({
            'Code': codes[1:-1],
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