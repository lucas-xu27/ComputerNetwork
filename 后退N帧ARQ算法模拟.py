import pygame
import random
import time

# 初始化 pygame
pygame.init()

# 设置窗口大小
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sliding Window Protocol Simulation")

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)

# 字体设置
font = pygame.font.Font(None, 30)

# 参数设置
TOTAL_FRAMES = 16  # 总帧数
WINDOW_SIZE = 7    # 滑动窗口大小
ACK_TIMEOUT = 4    # ACK 超时时间（秒）
LOSS_PROB = 0.1    # 数据帧丢失概率
CORRUPT_PROB = 0.1  # 数据帧损坏概率

# 日志设置
logs = []  # 保存日志的全局列表
MAX_LOG_LINES = 8  # 界面上显示的最大日志行数

def simulate_loss():
    return random.random() < LOSS_PROB

def simulate_corrupt():
    return random.random() < CORRUPT_PROB

class Sender:
    def __init__(self):
        self.sf = 0  # 发送窗口的起始帧
        self.sn = 0  # 下一个待发送的帧编号
        self.timers = {}  # 计时器字典，用于记录每帧的发送时间

    def send_frame(self):
        if self.sn < self.sf + WINDOW_SIZE and self.sn < TOTAL_FRAMES:
            if simulate_loss():
                log_message(f"Frame {self.sn % (WINDOW_SIZE + 1)} lost at sender")
                return None
            elif simulate_corrupt():
                log_message(f"Frame {self.sn % (WINDOW_SIZE + 1)} corrupted at sender")
                return None
            else:
                log_message(f"Sender sent frame {self.sn % (WINDOW_SIZE + 1)}")
            self.timers[self.sn] = time.time()
            self.sn += 1
            return self.sn - 1

    def check_timeouts(self):
        if self.sf in self.timers and time.time() - self.timers[self.sf] > ACK_TIMEOUT:
            log_message(f"Timeout for frame {self.sf % (WINDOW_SIZE + 1)}, retransmitting")
            self.sn = self.sf  # 重置发送指针
            del self.timers[self.sf]  # 重置计时器

    def process_ack(self, frame):
        if frame >= self.sf and frame < self.sf + WINDOW_SIZE:
            log_message(f"Sender received ACK for frame {frame % (WINDOW_SIZE + 1)}")
            self.sf = frame + 1  # 滑动窗口起点
            if frame in self.timers:
                del self.timers[frame]

    def draw(self):
        for i in range(TOTAL_FRAMES):
            x = 50 + i * 45
            y = 100
            if i < self.sf:
                color = BLUE
            elif self.sf <= i < self.sn:
                color = GREEN
            elif i == self.sn:
                color = RED
            elif self.sf <= i < self.sf + WINDOW_SIZE:
                color = YELLOW
            else:
                color = GRAY
            pygame.draw.rect(screen, color, (x, y, 40, 40))
            text = font.render(str(i % (WINDOW_SIZE + 1)), True, BLACK)
            screen.blit(text, (x + 10, y + 5))

class Receiver:
    def __init__(self):
        self.rn = 0  # 接收方期望接收的帧编号

    def receive_frame(self, frame):
        if frame == self.rn:
            if simulate_loss():
                log_message(f"Frame {frame % (WINDOW_SIZE + 1)} lost at receiver")
                return None
            elif simulate_corrupt():
                log_message(f"Frame {frame % (WINDOW_SIZE + 1)} corrupted at receiver")
                return None
            else:
                log_message(f"Receiver received frame {frame % (WINDOW_SIZE + 1)}")
                self.rn += 1
                return frame  # 返回 ACK
        elif frame > self.rn:
            log_message(f"Receiver out of order frame {frame % (WINDOW_SIZE + 1)}, discarded")
        return None

    def draw(self):
        for i in range(TOTAL_FRAMES):
            x = 50 + i * 45
            y = 300
            if i < self.rn:
                color = BLUE
            elif i == self.rn:
                color = RED
            else:
                color = GRAY
            pygame.draw.rect(screen, color, (x, y, 40, 40))
            text = font.render(str(i % (WINDOW_SIZE + 1)), True, BLACK)
            screen.blit(text, (x + 10, y + 5))

def draw_log():
    pygame.draw.rect(screen, WHITE, (50, 480, 800, 80))  # 清除日志区域
    y_offset = 0
    for log in logs[-MAX_LOG_LINES:]:
        log_text = font.render(log, True, BLACK)
        screen.blit(log_text, (50, 440 + y_offset))
        y_offset += 20

def log_message(message):
    logs.append(message)

# 主循环
def main():
    sender = Sender()
    receiver = Receiver()

    running = True
    paused = True
    clock = pygame.time.Clock()

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
        if paused:
            pause_text = font.render("Paused", True, RED)
            screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))

        if not paused:
            frame = sender.send_frame()
            if frame is not None:
                ack = receiver.receive_frame(frame)
                if ack is not None:
                    sender.process_ack(ack)
            sender.check_timeouts()

        sender.draw()
        receiver.draw()
        draw_log()

        pygame.display.flip()
        clock.tick(1)  # 控制帧率为 1 FPS

    pygame.quit()

if __name__ == "__main__":
    main()