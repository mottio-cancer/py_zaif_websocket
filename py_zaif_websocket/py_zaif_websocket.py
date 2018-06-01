#!/usr/bin/python3
# coding: utf-8

import websocket
import threading
import traceback
from time import sleep
import json
import logging

class ZaifWebsocket:

    MAX_LIMIT_LEN = 1000
    
    '''
    #
    # symbolに購読する通貨セットを指定してください
    # 'btc_jpy'など
    # recconect: エラー発生時に再接続するか否か
    #
    '''
    def __init__(self, 
                 endpoint="wss://ws.zaif.jp:8888/stream", 
                 symbol="btc_jpy", 
                 reconnect=False
                 ):
        # ロガー生成
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing WebSocket.")

        self.endpoint = endpoint
        self.symbol = symbol
        self.reconnect = reconnect # 再接続フラグ

        # データを格納する変数を宣言
        self.data = {}

        self.exited = False


        self.logger.info("Connecting to %s" % endpoint)
        self.__connect(self.endpoint, self.symbol)
        self.logger.info('Connected to WS.')

    def exit(self):
        '''WebSocketクローズ時に呼ばれます'''
        self.exited = True
        self.ws.close()

    def get_board_snapshot(self):
        return  { 
                    'asks': self.data['asks'],
                    'bids': self.data['bids'],
                }

    def get_ticker(self):
        last = self.data['last_price']['price']
        buy = self.data['asks'][0][0]
        sell = self.data['bids'][0][0]
        mid = round(buy + sell,1)
        return {
                'last': last,
                'buy': buy,
                'sell': sell,
                'mid': mid,
                }

    # TODO 注文情報をマージしよう。約定されたorder_idのセットも作ろう
    def get_execution(self, order_id=None):
        if order_id is None:
            return self.data['trades']
        else:
            retData = [ret for ret in self.data['trades'] if ret['tid'] == order_id]
            return retData

    #
    # End Public Methods
    #

    def __connect(self, endpoint, symbol):
        '''Connect to the websocket in a thread.'''
        self.logger.debug("Starting thread")
        
        wsURL = endpoint + "?currency_pair=" + symbol

        self.ws = websocket.WebSocketApp(wsURL,
                                         on_message=self.__on_message,
                                         on_close=self.__on_close,
                                         on_open=self.__on_open,
                                         on_error=self.__on_error,
                                         header=None)

        self.wst = threading.Thread(target=lambda: self.ws.run_forever())
        self.wst.daemon = True
        self.wst.start()
        self.logger.debug("Started thread")

        # Wait for connect before continuing
        conn_timeout = 5
        while not self.ws.sock or not self.ws.sock.connected and conn_timeout:
            sleep(1)
            conn_timeout -= 1
        if not conn_timeout:
            self.logger.error("Couldn't connect to WS! Exiting.")
            self.exit()
            raise websocket.WebSocketTimeoutException('Couldn\'t connect to WS! Exiting.')

    def __on_open(self, ws):
        '''コネクションオープン時の処理'''
        self.logger.debug("Websocket Opened.")

    def __on_close(self, ws):
        '''WebSocketクローズ時の処理'''
        self.logger.info('Websocket Closed')

    def __on_error(self, ws, error):
        '''WebSocketでエラーが発生したときの処理'''
        if not self.exited:
            self.logger.error("Error : %s" % error)
            if self.reconnect:
                # 再接続フラグが有効であれば再接続
                self.exit()
                self.__connect(self.endpoint, self.symbol)
                self.exited = False
            else:
                raise websocket.WebSocketException(error)

    def __on_message(self, ws, message):
        '''WebSocketがメッセージを取得したときの処理'''
        message = json.loads(message)
        self.logger.debug(json.dumps(message))
        try:
            self.data = message
        except:
            self.logger.error(traceback.format_exc())
    

if __name__ == '__main__':
    zws = ZaifWebsocket(symbol='btc_jpy')

