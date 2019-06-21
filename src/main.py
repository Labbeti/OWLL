from PyQt5.QtWidgets import QApplication, QLabel


def window():
    app = QApplication([])
    label = QLabel("Hello")
    label.show()
    app.exec()


def main():
    #terminal = Terminal()
    #terminal.launch()
    # gen_gensim_clust()
    window()


if __name__ == "__main__":
    main()
