import multiprocessing
import numpy as np
import time
import os
# from pycuda import driver, compiler, gpuarray, tools
# import pycuda.autoinit

# CPU Stress Test
def cpu_stress_test(duration):
    def cpu_worker():
        while True:
            pass

    print("Starting CPU stress test")
    processes = []
    for _ in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=cpu_worker)
        processes.append(p)
        p.start()

    time.sleep(duration)

    for p in processes:
        p.terminate()
        p.join()
    print("CPU stress test completed")

# GPU Stress Test
def gpu_stress_test(duration):
    print("Starting GPU stress test")
    kernel_code = """__global__ void stress(float *a, float *b, float *c) {
        int idx = threadIdx.x + blockIdx.x * blockDim.x;
        c[idx] = a[idx] * b[idx] + c[idx];
    }"""

    n = 1024 * 256
    a = np.random.randn(n).astype(np.float32)
    b = np.random.randn(n).astype(np.float32)
    c = np.zeros(n, dtype=np.float32)

    a_gpu = gpuarray.to_gpu(a)
    b_gpu = gpuarray.to_gpu(b)
    c_gpu = gpuarray.to_gpu(c)

    mod = compiler.SourceModule(kernel_code)
    stress = mod.get_function("stress")

    start_time = time.time()
    while time.time() - start_time < duration:
        stress(a_gpu, b_gpu, c_gpu, block=(256, 1, 1), grid=(n // 256, 1))

    print("GPU stress test completed")

# RAM Stress Test
def ram_stress_test(duration):
    print("Starting RAM stress test")
    data = []
    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            # Allocate 100MB chunks
            data.append(np.zeros((100_000_000,), dtype=np.float64))
            time.sleep(0.1)
    except MemoryError:
        print("Memory full during RAM stress test")
    finally:
        del data
    print("RAM stress test completed")

# SSD Stress Test
def ssd_stress_test(duration, file_path="temp_stress_test_file"):
    print("Starting SSD stress test")
    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            with open(file_path, "wb") as f:
                f.write(os.urandom(100_000_000))  # Write 100MB of random data
            with open(file_path, "rb") as f:
                f.read()
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
    print("SSD stress test completed")

if __name__ == "__main__":
    duration = 10  # Duration of each stress test in seconds

    cpu_stress_test(duration)
    gpu_stress_test(duration)
    ram_stress_test(duration)
    ssd_stress_test(duration)
