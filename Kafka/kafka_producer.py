from kafka import KafkaProducer  # pip install kafka-python
from json import dumps
import time

"""
bootstrap.servers   | Broker list를 나열
acks                | 메시지를 보낸 후 요청 완료 전 승인 수
                    | 손실과 성능의 트레이드 오프로 낮을 수록 성능은 좋고 손실이 커짐
                    | acks에 대한 설명은 다음 슬라이드에 설명
Buffer.memory       | 카프카에 데이터를 보내기전 잠시 대기할 수 있는 메모리
                    | [Byte] 기준
comporession.type   | 데이터를 압축하여 보낼 수 있음
                    | None, gzip, snappy, lz4 포맷들 중 하나 선택
retries             | 오류로 전송 실패한 데이터를 다시 보냄
batch.size          | 여러 데이터를 배치로 보내는 것을 시도함
                    | 장애 발생시 메시지 손실 가능성 존재
linger.ms           | 배치형태 작업을 위해 기다리는 시간 조정
                    | 배치 사이즈에 도달하면 옵션과 관계없이 전송
                    | 배치 사이즈가 도달하지 않아도 제한 시간 도달 시 메시지 전송
max.request.size    | 한번에 보낼 수 있는 메시지 바이트 사이즈 (Default : 1MB)
"""

producer = KafkaProducer(acks=0,
                         compression_type='gzip',
                         bootstrap_servers=['localhost:9092'],
                         value_serializer=lambda x: dumps(x).encode('utf-8'))
start = time.time()
for i in range(10000):
    data = {'str' : 'result'+str(i)}
    producer.send('test', value=data)
    producer.flush()
print("elapsed :", time.time() - start)
