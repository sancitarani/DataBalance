import matplotlib
matplotlib.use('Agg')
from flask import render_template, request, Blueprint
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import numpy as np

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files or not request.files['file'].filename:
            error = "Tidak ada file yang dipilih. Silakan pilih file untuk diunggah."
            return render_template('_results.html', error=error), 400

        file = request.files['file']
        
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.filename.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file)
            else:
                error = "Tipe file tidak valid. Harap unggah file .csv, .xls, atau .xlsx."
                return render_template('_results.html', error=error), 400

            # --- Analisis Data ---
            target_column = 'Class'

            if target_column not in df.columns:
                error = f"Kolom target '{target_column}' tidak ditemukan di dalam file."
                return render_template('_results.html', error=error), 400
            
            if df[target_column].nunique() < 2:
                error = f"Kolom target '{target_column}' harus memiliki setidaknya 2 kelas unik untuk analisis."
                return render_template('_results.html', error=error), 400

            value_counts = df[target_column].value_counts()
            total_samples = len(df)
            
            class_details = []
            for class_name, count in value_counts.items():
                percentage = (count / total_samples) * 100
                is_majority = count == value_counts.max()
                is_minority = count == value_counts.min()
                label = ""
                if is_majority:
                    label = "Mayoritas"
                elif is_minority:
                    label = "Minoritas"

                class_details.append({
                    'name': class_name,
                    'count': count,
                    'percentage': f"{percentage:.1f}%",
                    'label': label
                })

            # Menggunakan Degree of Imbalance untuk logika dan tampilan
            degree_of_imbalance = value_counts.min() / total_samples
            
            majority_perc = (value_counts.max() / total_samples) * 100
            minority_perc = (value_counts.min() / total_samples) * 100
            distribution_difference = majority_perc - minority_perc

            # --- Visualisasi ---
            plt.style.use('seaborn-v0_8-whitegrid')
            
            # Bar Chart Frekuensi
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            value_counts.plot(kind='bar', ax=ax1, color='#3498db')
            ax1.set_title('Distribusi Frekuensi Kelas', fontsize=16)
            ax1.set_xlabel('Kelas', fontsize=12)
            ax1.set_ylabel('Frekuensi', fontsize=12)
            ax1.tick_params(axis='x', rotation=0)
            bar_chart_img = save_plot_to_base64(fig1)

            # Pie Chart Proporsi
            fig2, ax2 = plt.subplots(figsize=(8, 8))
            ax2.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', startangle=140, colors=['#3498db', '#2ecc71', '#e74c3c', '#f1c40f', '#9b59b6'])
            ax2.set_title('Proporsi Kelas', fontsize=16)
            pie_chart_img = save_plot_to_base64(fig2)

            # --- Kesimpulan dan Saran ---
            analysis_result = get_analysis_result(degree_of_imbalance)
            analysis_result['class_details'] = class_details
            analysis_result['key_stats'] = {
                'total_samples': total_samples,
                'num_classes': len(value_counts),
                'degree_of_imbalance': f"{degree_of_imbalance:.2%}",
                'distribution_difference': f"{distribution_difference:.1f}%"
            }

            return render_template('_results.html', 
                                   bar_chart=bar_chart_img, 
                                   pie_chart=pie_chart_img,
                                   analysis=analysis_result)

        except Exception as e:
            error = f"Terjadi kesalahan saat memproses file Anda: {e}"
            return render_template('_results.html', error=error), 500

    return render_template('index.html')

def save_plot_to_base64(fig):
    """Menyimpan plot matplotlib ke dalam format base64 untuk ditampilkan di HTML."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_str

def get_analysis_result(ratio):
    """Memberikan kesimpulan dan saran berdasarkan rasio ketidakseimbangan."""
    result = {}
    # Mild: 20-40%
    if 0.2 <= ratio <= 0.4:
        result['category'] = "Mild Imbalance"
        result['description'] = "Tingkat ketidakseimbangan ringan terdeteksi. Perlakuan khusus mungkin tidak diperlukan, tetapi perlu diwaspadai."
        result['recommendation_key'] = "none"
    # Moderate: 1-20%
    elif 0.01 <= ratio < 0.2:
        result['category'] = "Moderate Imbalance"
        result['description'] = "Dataset Anda memiliki tingkat ketidakseimbangan kelas sedang. Ini dapat membiaskan model machine learning Anda terhadap kelas mayoritas."
        result['recommendation_key'] = "smote_adasyn"
    # Severe: <1%
    elif ratio < 0.01:
        result['category'] = "Extreme Imbalance"
        result['description'] = "Dataset Anda memiliki ketidakseimbangan kelas yang ekstrem. Ini akan secara signifikan berdampak pada kinerja model, kemungkinan besar menyebabkan pengenalan kelas minoritas yang buruk."
        result['recommendation_key'] = "kn_smote"
    # Balanced: > 40%
    else:
        result['category'] = "Balance"
        result['description'] = "Distribusi kelas dalam dataset Anda tampak seimbang. Tidak ada perlakuan khusus yang diperlukan untuk menangani ketidakseimbangan kelas."
        result['recommendation_key'] = "none"
    return result
