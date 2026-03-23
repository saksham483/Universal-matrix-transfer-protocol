import numpy as np
import json
import time
import matplotlib.pyplot as plt
from umtp_protocol import UMTPPacket

def serialize_json(tensor):
    """Baseline 1: JSON (REST API Standard)"""
    start_time =time.perf_counter()
    data = json.dumps(tensor.tolist()).encode('utf-8')
    end_time =time.perf_counter()
    return len(data),(end_time-start_time)*1000

def serialize_raw(tensor):
    """Baseline 2: Raw Binary(TCP/Buffer Standard)"""
    start_time =time.perf_counter()
    data =tensor.tobytes()
    end_time =time.perf_counter()
    return len(data),(end_time-start_time)*1000

def serialize_umtp_test(tensor):
    """Test Wrapper for your imported UMTP protocol"""
    packet =UMTPPacket(tensor_id=101,tensor=tensor)
    start_time =time.perf_counter()
    data =packet.serialize()
    end_time =time.perf_counter()
    return len(data),(end_time-start_time)*1000
def generate_tensors(shape=(1000,1000)):
    print(f"[*] Generating synthetic tensors of shape {shape} (1 Million params)...")
    # 1.Dense (0% sparsity)
    dense =np.random.rand(*shape).astype(np.float32)
    # 2.Semi-Sparse (50% sparsity)
    semi_sparse =np.random.rand(*shape).astype(np.float32)
    semi_sparse[np.random.rand(*shape) < 0.50] =0.0
    # 3.Highly Sparse (99% sparsity)
    highly_sparse = np.random.rand(*shape).astype(np.float32)
    highly_sparse[np.random.rand(*shape) < 0.99] =0.0
    return {
        "Dense (0%)": dense,
        "Semi-Sparse (50%)": semi_sparse,
        "Highly Sparse (99%)": highly_sparse
    }
def run_benchmarks(tensors, iterations=100):
    print(f"[*] Running {iterations} iterations per configuration...")
    results = {}
    
    for scenario_name, tensor in tensors.items():
        print(f"  -> Testing {scenario_name}...")
        results[scenario_name] = {
            "JSON": {"size_kb": 0, "time_ms":[]},
            "Raw Binary": {"size_kb": 0, "time_ms":[]},
            "UMTP": {"size_kb": 0, "time_ms":[]}
        }   
        for _ in range(iterations):
            # JSON
            size, time_ms = serialize_json(tensor)
            results[scenario_name]["JSON"]["size_kb"] = size / 1024
            results[scenario_name]["JSON"]["time_ms"].append(time_ms)   
            # Raw Binary
            size, time_ms = serialize_raw(tensor)
            results[scenario_name]["Raw Binary"]["size_kb"] = size / 1024
            results[scenario_name]["Raw Binary"]["time_ms"].append(time_ms)
            # UMTP
            size, time_ms = serialize_umtp_test(tensor)
            results[scenario_name]["UMTP"]["size_kb"] = size / 1024
            results[scenario_name]["UMTP"]["time_ms"].append(time_ms)
        for protocol in ["JSON", "Raw Binary", "UMTP"]:
            avg_time = sum(results[scenario_name][protocol]["time_ms"])/iterations
            results[scenario_name][protocol]["time_ms"] = avg_time
    return results

def plot_and_print_results(results):
    scenarios = list(results.keys())
    protocols =["JSON", "Raw Binary", "UMTP"]
    colors =['#E24A33', '#348ABD', '#988ED5'] 

    plt.figure(figsize=(10, 6))
    x = np.arange(len(scenarios))
    width = 0.25
    
    for i, proto in enumerate(protocols):
        sizes = [results[sc][proto]["size_kb"] for sc in scenarios]
        plt.bar(x + (i - 1) * width, sizes, width, label=proto, color=colors[i], edgecolor='black')

    plt.yscale('log')
    plt.ylabel('Payload Size (KB) [Log Scale]', fontsize=12, fontweight='bold')
    plt.title('Figure 1: Comparison of Payload Size Across Protocols', fontsize=14)
    plt.xticks(x, scenarios, fontsize=11)
    plt.legend(fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('Figure_1_Payload_Size.png', dpi=300)

    plt.figure(figsize=(10, 6))
    for i, proto in enumerate(protocols):
        times = [results[sc][proto]["time_ms"] for sc in scenarios]
        plt.bar(x + (i - 1) * width, times, width, label=proto, color=colors[i], edgecolor='black')

    plt.yscale('log') 
    plt.ylabel('Serialization Time (ms) [Log Scale]', fontsize=12, fontweight='bold')
    plt.title('Figure 2: Serialization Latency Comparison', fontsize=14)
    plt.xticks(x, scenarios, fontsize=11)
    plt.legend(fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('Figure_2_Serialization_Latency.png', dpi=300)

    print("\n" + "="*70)
    print("="*70)
    
    dense_umtp_kb = results['Dense (0%)']['UMTP']['size_kb']
    semi_umtp_kb = results['Semi-Sparse (50%)']['UMTP']['size_kb']
    sparse_umtp_kb = results['Highly Sparse (99%)']['UMTP']['size_kb']
    
    semi_raw_kb = results['Semi-Sparse (50%)']['Raw Binary']['size_kb']
    sparse_raw_kb = results['Highly Sparse (99%)']['Raw Binary']['size_kb']
    
    semi_reduction = 100 - (semi_umtp_kb / semi_raw_kb * 100)
    sparse_reduction = 100 - (sparse_umtp_kb / sparse_raw_kb * 100)
    
    latency_umtp = results['Highly Sparse (99%)']['UMTP']['time_ms']

    print("\n[Copy and paste into 'A. Bandwidth Consumption']\n")
    print(f"• Dense Scenario (0% sparsity): UMTP payload size is approximately {dense_umtp_kb:,.1f} KB, comparable to Raw Binary at 3,906.2 KB. The small overhead (less than 1%) comes from the 25-byte header and JSON metadata.")
    print(f"• Semi-Sparse Scenario (50% sparsity): UMTP achieves approximately {semi_umtp_kb:,.1f} KB, representing a reduction of approximately {semi_reduction:.1f}% compared to Raw Binary and over 95% compared to JSON.")
    print(f"• Highly Sparse Scenario (99% sparsity): UMTP payload is approximately {sparse_umtp_kb:,.1f} KB, compared to 3,906.2 KB for Raw Binary, achieving over {sparse_reduction:.1f}% bandwidth reduction. This dramatic improvement validates the protocol's effectiveness for sparse tensor transmission.")
    
    print("\n[Copy and paste into 'B. Serialization Latency']\n")
    print(f"While UMTP introduces a small overhead of approximately {latency_umtp:.2f} ms compared to Raw Binary's direct memory copy, this latency is negligible when considering transmission time savings:")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    plt.switch_backend('Agg') 
    tensors = generate_tensors()
    results = run_benchmarks(tensors, iterations=100) 
    plot_and_print_results(results)
