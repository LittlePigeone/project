style = '''
    QWidget {
        background-color: #0f0f4d;
        color: #b2aae6;
    }
    QTabWidget::pane { /* The tab widget frame */
        background-color: #e1e2fc;
        border: none;
        border-top: 1px solid black;
    }
    QTabWidget::tab-bar {
    alignment: center;
    }
    QTabBar::tab {
        background-color: #a1a1ec;
        color: #0c0d3a;
        font-size: 14px;
        font-weight: 300;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        margin: 10px;
        min-width: 80px;
        padding: 15px;
    }
    QTabBar::tab:selected {
        background-color: #8080e5;
        color: #f0f0fc;
        margin-bottom: -1px; 
    }
    QTabBar::tab:!selected {
        background: lightgray;
        color: blue;
        margin-top: 2px;
    }
    QTabBar::tab:hover {
        background-color: #8080e5;
        color: #f0f0fc;
    }
    QPushButton {
        background-color: #a1a1ec;
        color: #0c0d3a;
        font-size: 14px;
        font-weight: bold;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #8080e5;
        color: #f0f0fc;
    }
    QPushButton:pressed {
        background-color: #6484e9;
    }
    QLabel {
        color: #e1e2fc;
    }
'''