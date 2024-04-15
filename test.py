import concurrent.futures
import time


class MyClass:
    def __init__(self):
        pass

    def method1(self):
        print("Method 1 is running")
        time.sleep(2)  # 模拟耗时操作
        print("Method 1 finished")

    def method2(self):
        print("Method 2 is running")
        time.sleep(2)  # 模拟耗时操作
        print("Method 2 finished")

    def method3(self):
        print("Method 3 is running")
        time.sleep(4)  # 模拟耗时操作，这里假设它执行得比前两个方法快
        print("Method 3 finished")


def execute_methods_concurrently(obj):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            "method1": executor.submit(obj.method1),
            "method2": executor.submit(obj.method2),
            "method3": executor.submit(obj.method3),
        }

        # 等待method1和method2执行完成，不等待method3
        done, not_done = concurrent.futures.wait(
            [futures["method1"], futures["method2"]], return_when=concurrent.futures.FIRST_COMPLETED
        )
        if done:
            print("aa")
        if not_done:
            print("bb")
        # 此时，method1和method2已经完成，但method3可能仍在执行
        # print("Over")  # 在method1和method2完成后输出

        # 如果需要，可以等待method3也完成
        # concurrent.futures.wait([futures["method3"]])


def main():
    my_obj = MyClass()
    execute_methods_concurrently(my_obj)


if __name__ == "__main__":
    main()