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
def root(man: str, pin: str, sou: str, win_tile_str: str):
  print(man)
  tiles = TilesConverter.string_to_136_array(man=man, pin=pin, sou=sou)

  win_tile = get_win_tile(win_tile_str)
  melds = None
  dora_indicators = None
  config = None
  result = calculator.estimate_hand_value(tiles, win_tile, melds, dora_indicators, config)
  return result

def get_win_tile(tile_str: str):
  if re.match(r'^[1-9]', tile_str):
    tile_num, tile_type, has_aka = split_tile_str(tile_str)
    print(has_aka)
    match tile_type:
      case 'm':
        return TilesConverter.string_to_136_array(man=tile_num, has_aka_dora=has_aka)[0]
      case 'p':
        return TilesConverter.string_to_136_array(pin=tile_num, has_aka_dora=has_aka)[0]
      case 's':
        return TilesConverter.string_to_136_array(sou=tile_num, has_aka_dora=has_aka)[0]
  else:
    match tile_str:
      case 'ton':
        return EAST
      case 'nan':
        return SOUTH
      case 'sha':
        return WEST
      case 'pei':
        return NORTH
      case 'haku':
        return HAKU
      case 'hatsu':
        return HATSU
      case 'chun':
        return CHUN

# 1s ⇨ 1, sに分ける
def split_tile_str(tile_str: str):
  tile_num = re.findall(r'^([1-9])', tile_str)[0]
  tile_type = re.findall(r'^[1-9]([mps])', tile_str)[0]
  has_aka = re.match(r'^[1-9][mps]Red', tile_str) != None
  return tile_num, tile_type, has_aka
