from fastapi import FastAPI
from mahjong.hand_calculating.hand import HandCalculator
from mahjong.tile import TilesConverter
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
from mahjong.meld import Meld
from mahjong.constants import EAST, SOUTH, WEST, NORTH

app = FastAPI()
calculator = HandCalculator()

@app.get("/")
async def root():
  tiles = TilesConverter.string_to_136_array(man='234555', pin='555', sou='22555')
  win_tile = TilesConverter.string_to_136_array(sou='5')[0]
  melds = None
  dora_indicators = None
  config = None
  result = calculator.estimate_hand_value(tiles, win_tile, melds, dora_indicators, config)
  return result
