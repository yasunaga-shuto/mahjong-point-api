from fastapi import FastAPI
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.tile import TilesConverter
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
from mahjong.meld import Meld
from mahjong.constants import EAST, SOUTH, WEST, NORTH, HAKU, HATSU, CHUN
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import re

app = FastAPI()
calculator = HandCalculator()
origins = [
  "http://localhost:3000",
]
app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.get("/")
async def root(man: str, pin: str, sou: str, win_tile_str: str):
  print(man)
  tiles = TilesConverter.string_to_136_array(man=man, pin=pin, sou=sou)

  win_tile = None
  # 数牌の場合
  if re.match(r'^[1-9]', win_tile_str):
    win_tile = TilesConverter.string_to_136_array(sou=win_tile_str)[0]
  else:
    match win_tile_str:
      case 'ton':
        win_tile = EAST
      case 'nan':
        win_tile = SOUTH
      case 'sha':
        win_tile = WEST
      case 'pei':
        win_tile = NORTH
      case 'haku':
        win_tile = HAKU
      case 'hatsu':
        win_tile = HATSU
      case 'chun':
        win_tile = CHUN

  melds = None
  dora_indicators = None
  config = None
  result = calculator.estimate_hand_value(tiles, win_tile, melds, dora_indicators, config)
  return result
