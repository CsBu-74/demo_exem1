from dash import Dash, Output, Input, html, dcc
import pandas as pd
import plotly.express as px
import psutil
import numpy as np
import platform
import time

app = Dash(__name__)

CPU_COUNT = psutil.cpu_count()

# Инициализация DataFrame с историей значений CPU, RAM, диска и сети
history = pd.DataFrame()
for i in range(CPU_COUNT):
    history[f'cpu{i + 1}'] = [np.nan] * 100
history['ram'] = [np.nan] * 100
history['disk_usage'] = [np.nan] * 100
history['bytes_sent'] = [np.nan] * 100
history['bytes_recv'] = [np.nan] * 100

prev_bytes_sent = psutil.net_io_counters().bytes_sent
prev_bytes_recv = psutil.net_io_counters().bytes_recv
prev_time = time.time()

# Определение callback функции для обновления данных и построения графиков
def register_callbacks(app):
    @app.callback(
        Output("status", "children"),
        Output('graph_cpu', 'figure'),
        Output('cpu_info', 'children'),
        Output('graph_memory', 'figure'),
        Output('ram_info', 'children'),
        Output('graph_disk', 'figure'),
        Output('disk_info', 'children'),  # Добавлено для информации о диске
        Output('graph_network', 'figure'),
        Output("network_speeds", "children"),
        Input("timer", "n_intervals"),
        Input('cpu_checklist', 'value')  # Добавляем input для checklist
    )
    def update_status(n, selected_cpus):
        global history, prev_bytes_sent, prev_bytes_recv, prev_time

        # Получаем текущие данные о системе
        cpu = psutil.cpu_percent(percpu=True)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net_io = psutil.net_io_counters()

        current_time = time.time()
        elapsed_time = current_time - prev_time

        # Подсчет скорости передачи данных в сети
        upload_speed = (net_io.bytes_sent - prev_bytes_sent) / elapsed_time
        download_speed = (net_io.bytes_recv - prev_bytes_recv) / elapsed_time

        # Обновляем предыдущие значения
        prev_bytes_sent = net_io.bytes_sent
        prev_bytes_recv = net_io.bytes_recv
        prev_time = current_time

        # Обновление истории данных
        history = history.shift(periods=-1)
        history.iloc[-1, :CPU_COUNT] = cpu
        history.iloc[-1, CPU_COUNT] = ram.percent
        history.iloc[-1, CPU_COUNT + 1] = disk.percent  # Обновляем данные о диске
        history.iloc[-1, CPU_COUNT + 2] = upload_speed
        history.iloc[-1, CPU_COUNT + 3] = download_speed

        # Создание графиков
        fig_cpu = px.line(history.reset_index(), x=history.index, y=[f'cpu{i + 1}' for i in range(CPU_COUNT) if str(i + 1) in selected_cpus],
                          line_shape='spline')
        fig_cpu.update_layout(title_text='График загрузки процессора (CPU)')

        fig_memory = px.line(history.reset_index(), x=history.index, y=['ram'], line_shape='spline')
        fig_memory.update_layout(title_text='График использования RAM')

        # График использования диска
        fig_disk = px.line(history.reset_index(), x=history.index, y=['disk_usage'], line_shape='spline')
        fig_disk.update_layout(title_text='График использования диска')

        # График сетевой активности
        fig_network = px.line(history.reset_index(), x=history.index, y=['bytes_sent', 'bytes_recv'], line_shape='spline',
                              labels={'value': 'Скорость (Б/с)', 'variable': 'Тип данных'}, title='Сетевая активность')

        # Текстовые данные о скорости сети
        network_speeds_text = f"""
            Скорость отправки: {upload_speed:.2f} Б/с
            Скорость загрузки: {download_speed:.2f} Б/с
        """

        # Информация о процессоре
        cpu_info = {
            "Производитель": platform.processor(),
            "Архитектура": platform.architecture()[0],
            "Частота": f"{psutil.cpu_freq().max:.2f} MHz" if psutil.cpu_freq() else "N/A",
            "Количество ядер": CPU_COUNT
        }

        cpu_info_text = f"""
            Информация о процессоре:
                Производитель: {cpu_info['Производитель']}
                Архитектура: {cpu_info['Архитектура']}
                Частота: {cpu_info['Частота']}
                Количество ядер: {cpu_info['Количество ядер']}
        """

        # Информация о RAM
        ram_info_text = f"""
            Информация об оперативной памяти:
                Всего памяти: {ram.total / (1024 ** 3):.2f} GB
                Использовано памяти: {ram.used / (1024 ** 3):.2f} GB
                Свободно памяти: {ram.available / (1024 ** 3):.2f} GB
                Процент использования: {ram.percent}%
        """

        # Информация о диске
        disk_info_text = f"""
            Информация о диске:
                Всего пространства: {disk.total / (1024 ** 3):.2f} GB
                Использовано: {disk.used / (1024 ** 3):.2f} GB
                Свободно: {disk.free / (1024 ** 3):.2f} GB
                Процент использования: {disk.percent}%
        """

        return f"Интервалы: {n}", fig_cpu, cpu_info_text, fig_memory, ram_info_text, fig_disk, disk_info_text, fig_network, network_speeds_text

register_callbacks(app)

# Макет приложения
app.layout = html.Div([
    html.Div(id="status"),
    dcc.Checklist(
        id='cpu_checklist',
        options=[{'label': f'Ядро {i + 1}', 'value': str(i + 1)} for i in range(CPU_COUNT)],
        value=[str(i + 1) for i in range(CPU_COUNT)],  # По умолчанию отображаем все ядра
        inline=True
    ),
    dcc.Graph(id='graph_cpu'),
    html.Div(id='cpu_info'),
    dcc.Graph(id='graph_memory'),
    html.Div(id='ram_info'),
    dcc.Graph(id='graph_disk'),  # Добавлен график диска
    html.Div(id='disk_info'),  # Добавлен блок для информации о диске
    dcc.Graph(id='graph_network'),
    html.Div(id="network_speeds"),
    dcc.Interval(id='timer', interval=1000)  # Обновление каждую секунду
])


if __name__ == '__main__':
    app.run_server(debug=True, host="127.0.0.1", port=8050)
