import matplotlib.pyplot as plt

url_times = [420,390,450,510,470]
text_times = [310,295,330,340,315]

plt.figure(figsize=(10,6))
plt.plot(url_times, marker='o', label='URL Scan Time')
plt.plot(text_times, marker='o', label='Text Scan Time')

plt.title("PhishShield AI System Performance")
plt.xlabel("Test Run")
plt.ylabel("Response Time (ms)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("figure_6_6_performance.png", dpi=300)
plt.show()
