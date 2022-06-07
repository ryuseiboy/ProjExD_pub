import pygame as pg
import sys
import random
import math

### ([画像ファイルリスト], [選択肢リスト])を集めたリスト。
### 問題を追加する場合は同様に([画像ファイルリスト], [選択肢リスト])をリストの要素に追記する
### C0B21146 美尾 勇希
ques_list = [(["fig/shin.jpg","fig/ori.jpg","fig/zophi.jpg","fig/jack.jpg"],          
              ["シン・ウルトラマン","ウルトラマン","ゾフィー","ウルトラマンジャック"]),

             (["fig/kirin.png", "fig/raion.png", "fig/ti-ta-.png", "fig/tora.png"],
              ["キリン", "ライオン", "チーター", "トラ"]),

              (['fig/keppengin.jpg', 'fig/panda.jpg', 'fig/raion.jpg', 'fig/ressapanda.jpg'],
              ['ケープペンギン', 'パンダ', 'ライオン', 'レッサーパンダ'])
            ]
ques, choi = random.choice(ques_list)      #画像ファイルリスト, 選択肢リスト (ランダムな組み合わせが選ばれる)

but = [] #ボタン用リスト

jud = True
ans_jud = 0

isStart = False # スタートフラグ　青柳

isFinsh = False

class Screen(pg.sprite.Sprite): # Screen生成
  def __init__(self, col, wh, title):                    # 色,幅と高さ(タプル),タイトル
    super().__init__()
    #タイトル
    pg.display.set_caption(title) #BloQuiz
    # Surface
    self.width, self.height = wh
    self.disp = pg.display.set_mode((self.width, self.height))
    # Rect
    self.rect= self.disp.get_rect()                                 
    # 色変更
    self.disp.fill((col))

class Paddle(pg.sprite.Sprite): #Paddle生成
  def __init__(self,col,wh,sc):#色、幅と高さ（タプル）、スクリーン
    super().__init__()
    self.width,self.height = wh
    self.image = pg.Surface((self.width,self.height))
    self.color = col
    pg.draw.rect(self.image, self.color, (0,0,self.width,self.height))
    self.rect = self.image.get_rect()
    self.screen = sc #スクリーン参照
    self.rect.bottom = sc.rect.bottom -400
    self.update = self.start #初期状態にする
  
  def start(self): #初期状態関数
    global jud
    self.rect.centerx = pg.mouse.get_pos()[0]
    if jud == False:
      self.update = self.end

  def end(self): #ゲームオーバー時関数
    self.rect.centerx = self.screen.rect.centerx
    self.color = (255,0,0) #バーの色を変える
    pg.draw.rect(self.image, self.color, (0,0,self.width,self.height))


class Ball(pg.sprite.Sprite):
  global jud
  jud = True
  def __init__(self,col,r,pdl,blc,sc,speed,anglf,angri):
    super().__init__()
    self.image = pg.Surface((2*r, 2*r))
    self.image.set_colorkey((0, 0, 0))
    pg.draw.circle(self.image, col, (r, r), r)
    self.rect = self.image.get_rect()
    self.dx = self.dy = 0  # ボールの速度
    self.paddle = pdl  # パドルへの参照
    self.blocks = blc  # ブロックグループへの参照
    self.screen = sc #スクリーンへの参照
    self.update = self.start # ゲーム開始状態に更新
    #self.score = score
    self.hit = 0  # 連続でブロックを壊した回数
    self.speed = speed # ボールの初期速度
    self.angle_left = anglf # パドルの反射方向(左端:135度）
    self.angle_right = angri # パドルの反射方向(右端:45度）

  def start(self):
      global isStart
      # ボールの初期位置(パドルの上)
      self.rect.centerx = self.paddle.rect.centerx
      self.rect.bottom = self.paddle.rect.top

      # 左クリックでボール射出
      if pg.mouse.get_pressed()[0] == 1:
          isStart = True # スタートフラグをTrueに変更　青柳
          self.dx = 0
          self.dy = -self.speed
          self.update = self.move

  def end(self):
    global jud
    self.rect.centerx = self.paddle.rect.centerx
    self.rect.bottom = self.paddle.rect.top
    self.dx = 0
    self.dy =0
    pg.draw.circle(self.image, (255,100,0), (7, 7),7)
    jud = False
    
   # ボールの挙動
  def move(self):
    cnt =0
    self.rect.centerx += self.dx
    self.rect.centery += self.dy

    # 壁との反射
    if self.rect.left < self.screen.rect.left:    # 左側
        self.rect.left = self.screen.rect.left
        self.dx = -self.dx              # 速度を反転
        #print(self.dx)
    if self.rect.right >= self.screen.rect.right:  # 右側
        self.rect.right = self.screen.rect.right
        self.dx = -self.dx
    if self.rect.top <= self.screen.rect.top:      # 上側
        self.rect.top = self.screen.rect.top
        self.dy = -self.dy

    # パドルとの反射(左端:135度方向, 右端:45度方向, それ以外:線形補間)
    # 2つのspriteが接触しているかどうかの判定
    if self.rect.colliderect(self.paddle.rect) and self.dy > 0:
        self.hit = 0                                # 連続ヒットを0に戻す
        (x1, y1) = (self.paddle.rect.left- self.rect.width, self.angle_left)
        (x2, y2) = (self.paddle.rect.right, self.angle_right)
        x = self.rect.left                          # ボールが当たった位置
        y = (float(y2-y1)/(x2-x1)) * (x - x1) + y1  # 線形補間
        angle = math.radians(y)                     # 反射角度
        if cnt ==0:
          self.dx = -self.speed
          cnt+=1
        else:
          self.dx = self.dx * math.cos(angle)

        self.dy = -self.speed #* math.sin(angle)
        #print(self.speed)
        #self.paddle_sound.play()                    # 反射音

      # ボールを落とした場合
    if self.rect.top > self.screen.rect.bottom -370 or jud == False: # judフラグを追加　青柳
        self.update = self.end                    # ボールを初期状態に
        #self.gameover_sound.play()
        self.hit = 0
        #self.score.add_score(-100)                  # スコア減点-100点、ここをクイズ表示の判定変化にする
      
    # ボールと衝突したブロックリストを取得（Groupが格納しているSprite中から、指定したSpriteと接触しているものを探索）
    blocks_collided = pg.sprite.spritecollide(self, self.blocks, True)
    if blocks_collided:  # 衝突ブロックがある場合
        oldrect = self.rect
        for block in blocks_collided:
            # ボールが左からブロックへ衝突した場合
            if oldrect.left < block.rect.left and oldrect.right < block.rect.right:
                self.rect.right = block.rect.left
                self.dx = -self.dx
                
            # ボールが右からブロックへ衝突した場合
            if block.rect.left < oldrect.left and block.rect.right < oldrect.right:
                self.rect.left = block.rect.right
                self.dx = -self.dx

            # ボールが上からブロックへ衝突した場合
            if oldrect.top < block.rect.top and oldrect.bottom < block.rect.bottom:
                self.rect.bottom = block.rect.top
                self.dy = -self.dy

            # ボールが下からブロックへ衝突した場合
            if block.rect.top < oldrect.top and block.rect.bottom < oldrect.bottom:
                self.rect.top = block.rect.bottom
                self.dy = -self.dy
            #self.block_sound.play()     # 効果音を鳴らす
            self.hit += 1               # 衝突回数


class Block(pg.sprite.Sprite):#ブロッククラス
    def __init__(self, col, wh, xy, sc): #色、幅と高さ（タプル）、xy座標（タプル）、参照スクリーン
      super().__init__()
      self.width,self.height = wh
      self.image = pg.Surface((self.width,self.height))
      pg.draw.rect(self.image, col, (0,0,self.width,self.height),width=1)
      self.rect = self.image.get_rect()
      self.x,self.y = xy
      # ブロックの左上座標
      self.rect.left = sc.rect.left + self.x * self.rect.width
      self.rect.top = sc.rect.top + self.y * self.rect.height

class Question(pg.sprite.Sprite): #出題用画像クラス
  def __init__(self,fn,r,sc):#ファイル名、拡大率、参照スクリーン
    super().__init__()
    self.image = pg.image.load(fn)
    self.image = pg.transform.rotozoom(self.image, 0, r)
    self.rect = self.image.get_rect()
    self.rect.left = sc.rect.left
    self.rect.top = sc.rect.top

class OutWall(pg.sprite.Sprite):
  def __init__(self,wh,col):
    super().__init__()
    self.width,self.height = wh
    self.image = pg.Surface((self.width,self.height))
    pg.draw.rect(self.image, col, (0,0,self.width,self.height))
    self.rect = self.image.get_rect()
    self.rect.topleft = (0, 510)

class Button(pg.sprite.Sprite): #ボタン用クラス
  def __init__(self,wh,col,sc,y,num1,num2): 
    #幅と高さ（タプル）、色、参照スクリーン、y座標、正解判定用ボタンナンバー、正解判定ナンバー
    super().__init__()
    self.width,self.height = wh
    self.image = pg.Surface((self.width,self.height))
    self.col = col
    self.screen = sc
    pg.draw.rect(self.image, self.col, (0,0,self.width,self.height))
    self.rect = self.image.get_rect()
    self.y =y
    self.num1 = num1
    self.num2 = num2
    self.rect.centerx = self.screen.rect.centerx
    self.rect.bottom = self.screen.rect.centery + self.y

  def push(self): #ボタンが押された時の処理
    global ans_jud
    if self.num1 == self.num2:
      pg.draw.rect(self.image, (255,100,0), (0,0,self.width,self.height))
      ans_jud = 2
    else:
      pg.draw.rect(self.image, (100,100,100), (0,0,self.width,self.height))
      ans_jud = 1

class Text(pg.sprite.Sprite): #テキスト用クラス
  def __init__(self,text,x,y,col, s): 
    #テキスト、y座標、色、参照スクリーン #x,y,sを追加　x:x座標、y:y座標、s:文字サイズ　青柳
    super().__init__()
    font = pg.font.Font("ipaexg.ttf", s)
    self.image = font.render(text, True, col)
    self.rect = self.image.get_rect()
    self.rect.centerx = x
    self.rect.bottom = y 

def main():
  global jud, isFinsh
  num = random.randint(0,3) #正解判定用ナンバー
  clock = pg.time.Clock()
  screen = Screen((0,0,0),(450,900),"BloQuiz")
  
  time_count = 30 # 時間を追加　青柳
  pg.time.set_timer(pg.USEREVENT, 1000) # タイマーセット　青柳
  txt = f'残り時間{time_count}秒'

  paddle = Paddle((0,255,0),(74,5),screen)
  screen.disp.blit(paddle.image, paddle.rect)

  2
  #当たったらだめの壁を生成
  kabe=OutWall((screen.rect.width, 5),(250,0,0))

  question =Question((ques[num]),1,screen)
  screen.disp.blit(question.image,question.rect)
  
  # ブロックの作成(10*22)
  blos = pg.sprite.Group()                      
  for x in range(1, 11):
    for y in range(1, 23):
      #screenを問題画像にする
      blos.add(Block((0,255,0), (37.5,18), (x,y), question)) 

  ball = Ball((0,255,100),7,paddle,blos,screen,1.5,135,45)
  screen.disp.blit(ball.image, ball.rect) 

  #ボタンの作成
  cnt =0
  button1 = Button((300,50),(50,220,220),screen,120,0,num)
  but.append(button1)
  button2 = Button((300,50),(50,220,220),screen,190,1,num)
  but.append(button2)
  button3 = Button((300,50),(50,220,220),screen,260,2,num)
  but.append(button3)
  button4 = Button((300,50),(50,220,220),screen,330,3,num)
  but.append(button4)
  for i in range(4):
    screen.disp.blit(but[i].image, but[i].rect)

  #テキストの設定
  texts = pg.sprite.Group()
  cont =0
  for i in range(110,321,70):
    texts.add(Text(choi[cont],screen.rect.centerx,screen.rect.centery + i,(255,255,255), 30))
    cont += 1
 
  while True:
    screen.disp.fill((0,0,0))            # Screen画像更新

    screen.disp.blit(question.image,question.rect) #question画像更新

    paddle.update()                               # paddleの位置更新
    screen.disp.blit(paddle.image, paddle.rect)           # paddle画像更新

    if isFinsh == False:
      blos.draw(screen.disp) #ブロック画像更新

    ball.update() #ballの位置更新
    screen.disp.blit(ball.image,ball.rect) #ball画像更新

    for i in range(4):
      screen.disp.blit(but[i].image, but[i].rect)
      but[i].update()

    texts.draw(screen.disp)

    for event in pg.event.get():
      if event.type == pg.QUIT: return               # ✕ボタンでmain関数から戻る
      #マウス左クリック判定かつボールが落下していないか判定
      if event.type == pg.MOUSEBUTTONDOWN and jud == False: 
        for i in range(4):
          if but[i].rect.collidepoint(event.pos): #左クリックされた位置がボタン内であるか判定
            but[i].push() #ボタンを被push状態にする
          if ans_jud != 0: #解答されたかどうか判定
            but[0].push()
            but[1].push()
            but[2].push()
            but[3].push()
            isFinsh = True
      # isStartとjudがTrueの場合タイマー開始 青柳
      if isStart and jud:
        if event.type == pg.USEREVENT:
          time_count -= 1
          txt = f'残り時間{time_count}秒'

    if time_count <= 0: # タイマーが0になった場合judがFalseに変更　青柳
      jud = False

    if jud:
      text = Text(txt, 400, 20, (0, 0, 0), 15) # テキスト設定　黒　青柳
    else:
      text = Text(txt, 400, 20, (255, 0, 0), 15) #テキスト設定　赤　青柳
    screen.disp.blit(text.image, text.rect)
    screen.disp.blit(kabe.image,kabe.rect)

    pg.display.update()  # 画面の更新
    clock.tick(1000) 

if __name__ == "__main__":
    pg.init() 
    main()
    pg.quit()
    sys.exit()
