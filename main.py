from multiprocessing import Process
from g2g import site_1_actions

def start_action(browser_index):
    """
    Her işlem için farklı bir tarayıcı ve farklı bir ilan üzerinde çalışır.
    browser_index: Hangi tarayıcı profilinin kullanılacağını belirler.
    """
    site_1_actions(browser_index)

def main():
    processes = []
    
    # Aynı anda 5 farklı tarayıcı ve işlem başlatıyoruz
    for browser_index in range(5):  # 5 farklı tarayıcı için döngü
        process = Process(target=start_action, args=(browser_index,))
        processes.append(process)
        process.start()

    # İşlemlerin tamamlanmasını bekliyoruz
    for process in processes:
        process.join()

if __name__ == "__main__":
    main()
