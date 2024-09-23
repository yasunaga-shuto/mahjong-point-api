from fastapi import FastAPI, Request, status
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.tile import TilesConverter
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
from mahjong.meld import Meld
from mahjong.constants import EAST, SOUTH, WEST, NORTH, HAKU, HATSU, CHUN, FIVE_RED_MAN
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import re
from pydantic import BaseModel
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

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

class Hand(BaseModel):
  man: str
  pin: str
  sou: str
  honors: str
  win_tile: str
  dora_indicators: List[str]

@app.post("/")
def root(hand: Hand):
  tiles = TilesConverter.string_to_136_array(man=hand.man, pin=hand.pin, sou=hand.sou, honors=hand.honors, has_aka_dora=True)

  win_tile = convert_str_to_tile(hand.win_tile)
  melds = None
  dora_indicators = []
  for d in hand.dora_indicators:
    tile = convert_str_to_tile(d)
    dora_indicators.append(tile)

  config = None
  result = calculator.estimate_hand_value(tiles, win_tile, melds, dora_indicators, config)
  return result

def convert_str_to_tile(tile_str: str):
  tile_num, tile_type = split_tile_str(tile_str)
  match tile_type:
    case 'm':
      return TilesConverter.string_to_136_array(man=tile_num, has_aka_dora=True)[0]
    case 'p':
      return TilesConverter.string_to_136_array(pin=tile_num, has_aka_dora=True)[0]
    case 's':
      return TilesConverter.string_to_136_array(sou=tile_num, has_aka_dora=True)[0]
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
  tile_num = re.findall(r'^([1-9])', tile_str)
  if len(tile_num) <= 0:
    return tile_str, tile_str

  tile_type = re.findall(r'^[1-9]([mps])', tile_str)
  if len(tile_type) <= 0:
    return tile_str, tile_str

  has_aka = re.match(r'^[1-9][mps]Red', tile_str) != None
  if has_aka:
    return 'r', tile_type
  return tile_num[0], tile_type[0]

@app.exception_handler(RequestValidationError)
async def handler(request:Request, exc:RequestValidationError):
    print(exc)
    return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
