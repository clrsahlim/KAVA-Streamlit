# KAVA Resume Analytics Dashboard 🪪
Dashboard ini menampilkan analisis data resume dari berbagai kategori, mencakup distribusi hubungan pendidikan dengan kategori pekerjaan (menghitung kandidat yang memiliki pekerjaan relevan dengan latar belakang pendidikan) , distribusi keahlian untuk setiap kategori pekerjaan, dan distribusi jumlah sertifikat yang dimiliki kandidate per kategori pekerjaan.

## Live Demo
Access the dashboard directly at:
**[https://kava-analytics.streamlit.app/](https://kava-analytics.streamlit.app/)**

## Setup Environment - Anaconda
```
conda create --name main-ds python=3.11
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run Streamlit App
```
streamlit run dashboard.py
```

