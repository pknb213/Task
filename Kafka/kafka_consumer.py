from kafka import KafkaConsumer
from json import loads
from time import sleep

"""
bootstrap_servers   | 카프카 클러스터들의 호스트와 포트 정보 리스트 
auto_offset_reset   | earliest : 가장 초기 오프셋값
                    | latest : 가장 마지막 오프셋값
                    | none : 이전 오프셋값을 찾지 못할 경우 에러 
enable_auto_commit  | 주기적으로 offset을 auto commit 
group_id            | 컨슈머 그룹을 식별하기 위한 용도 
value_deserializer  | producer에서 value를 serializer를 했기 때문에 사용 
consumer_timeout_ms | 이 설정을 넣지 않으면 데이터가 없어도 오랜기간 connection한 상태가 된다. 
                    | 데이터가 없을 때 빠르게 종료시키려면 timeout 설정을 넣는다.
"""

# topic, broker list
consumer = KafkaConsumer(
    "filebeat_iot",
    bootstrap_servers=['13.125.246.197:9092', '52.79.215.253:9092', '52.79.250.228:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='testing',
    value_deserializer=lambda x: loads(x.decode('utf-8')),
    consumer_timeout_ms=1000
)

# get the consumer list
print('[Begin] Get consumer list')
for message in consumer:
    sleep(1)
    print("Topic: {0}, Partition: {1}, Offset: {2}, Key: {3}, Value: {4}".format(
        message.topic, message.partition, message.offset, message.key, message.value))
print('[End] Get consumer list')
