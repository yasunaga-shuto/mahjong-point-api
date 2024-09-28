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

class HandMeld(BaseModel):
  type: str
  pai: List[str]

class Hand(BaseModel):
  man: str
  pin: str
  sou: str
  honors: str
  win_tile: str
  dora_indicators: List[str]
  melds: List[HandMeld] = None
  has_aka_dora: bool
  is_riichi: bool
  player_wind: str
  round_wind: str

@app.post("/")
def root(hand: Hand):
  tiles = TilesConverter.string_to_136_array(man=hand.man, pin=hand.pin, sou=hand.sou, honors=hand.honors, has_aka_dora=True)
  print(hand)

  win_tile = convert_str_to_tile(hand.win_tile)
  melds = []
  # 鳴き
  for m in hand.melds:
    match m.type:
      case 'chi':
        chi_tiles = []
        for p in m.pai:
          tile = convert_str_to_tile(p)
          chi_tiles.append(tile)
        melds.append(Meld(meld_type=Meld.CHI, tiles=chi_tiles))
      case 'pon':
        pon_tiles = []
        for p in m.pai:
          tile = convert_str_to_tile(p)
          pon_tiles.append(tile)
        melds.append(Meld(meld_type=Meld.PON, tiles=pon_tiles))
      case 'ankan':
        melds.append(get_kan_tiles(m.pai[1], hand.has_aka_dora, False))
      case 'kan':
        melds.append(get_kan_tiles(m.pai[1], hand.has_aka_dora, True))

  print(melds)

  # ドラ
  dora_indicators = []
  for d in hand.dora_indicators:
    tile = convert_str_to_tile(d)
    dora_indicators.append(tile)

  config = HandConfig(
    is_riichi=hand.is_riichi,
    player_wind=convert_wind(hand.player_wind),
    round_wind=convert_wind(hand.round_wind),
    options=OptionalRules(has_open_tanyao=True, has_aka_dora=True),
  )
  result = calculator.estimate_hand_value(tiles, win_tile, melds, dora_indicators, config)
  return result

def convert_wind(wind_str: str):
  match wind_str:
    case 'ton':
      return EAST
    case 'nan':
      return SOUTH
    case 'sha':
      return WEST
    case 'pei':
      return NORTH

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

def get_kan_tiles(tile_str: str, has_aka_dora: bool, open: bool):
  tile_num, tile_type = split_tile_str(tile_str)
  if tile_num == '5' and has_aka_dora:
    match tile_type:
      case 'm':
        return Meld(Meld.KAN, TilesConverter.string_to_136_array(man='r555', has_aka_dora=True), open)
      case 'p':
        return Meld(Meld.KAN, TilesConverter.string_to_136_array(pin='r555', has_aka_dora=True), open)
      case 's':
        return Meld(Meld.KAN, TilesConverter.string_to_136_array(sou='r555', has_aka_dora=True), open)
  else:
    tile = convert_str_to_tile(tile_str)
    kan_tiles = [tile, tile, tile, tile]
    return Meld(Meld.KAN, kan_tiles, open)

@app.exception_handler(RequestValidationError)
async def handler(request:Request, exc:RequestValidationError):
    print(exc)
    return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
