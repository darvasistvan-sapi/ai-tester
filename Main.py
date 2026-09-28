from RunPodClient import RunPodClient

client = RunPodClient()

answer = client.send("What is 2 + 2?")
print(answer)
