# blktest

**blktest** — это легковесный инструмент для автоматизированного профилирования задержек (latency) блочных устройств в зависимости от глубины очереди (IO Depth).

Инструмент разработан для SRE и Backend-инженеров для быстрой и "честной" оценки производительности дисковой подсистемы (SSD/NVMe/EBS) перед деплоем I/O-intensive приложений (PostgreSQL, Kafka, ElasticSearch).

### Особенности
*   **Zero-Dependency**: Написан на чистом Python 3 (использует только стандартную библиотеку), не требует `pip install`.
*   **True Hardware Benchmark**: Использует `fio` с флагом `--direct=1` и движком `libaio` для обхода страничного кэша ОС (Page Cache).
*   **Automated Scaling**: Автоматически прогоняет тесты с нарастающим `iodepth` (от 1 до 256).
*   **Instant Visualization**: Генерирует график (PNG) через `gnuplot` сразу после завершения теста.

---

### 🛠 Технический стек
*   **Core**: [fio](https://github.com/axboe/fio) (Flexible I/O Tester)
*   **Orchestration**: Python 3.x (`subprocess`, `json`, `argparse`)
*   **Visualization**: [gnuplot](http://www.gnuplot.info/)
*   **IO Engine**: Linux AIO (`libaio`)
*   **Workload**: Random Read / Random Write (4k blocks)

---

### Требования

Утилита является оберткой (wrapper) над системными инструментами. Убедитесь, что они установлены в системе.

**Debian/Ubuntu:**
```bash
sudo apt-get update && sudo apt-get install -y fio gnuplot