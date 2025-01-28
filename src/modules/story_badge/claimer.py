from typing import Optional
from time import time

from eth_account.messages import encode_defunct
from loguru import logger
import pyuseragents

from config import RETRIES, PAUSE_BETWEEN_RETRIES
from src.utils.common.wrappers.decorators import retry
from src.utils.request_client.client import RequestClient
from src.utils.user.account import Account
from src.utils.proxy_manager import Proxy


class Story(Account, RequestClient):
    def __init__(
            self,
            private_key: str,
            proxy: Proxy | None):
        Account.__init__(self, private_key=private_key, proxy=proxy)
        RequestClient.__init__(self, proxy=proxy)

        self.headers = {
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://claim.story.foundation',
            'priority': 'u=1, i',
            'referer': 'https://claim.story.foundation/',
            'user-agent': pyuseragents.random(),
        }

    def __str__(self) -> str:
        return f'[{self.wallet_address}] | Claiming badge...'

    async def check_if_eligible(self) -> Optional[bool | str]:
        params = {
            'wallet': self.wallet_address,
        }

        response_json, status = await self.make_request(
            method="GET",
            headers=self.headers,
            url='https://cm-mint.odyssey.storyapis.com/api/check_wallet',
            params=params
        )

        if status == 200:
            if response_json['status'] == 'can_claim':
                return True
            elif response_json['status'] == 'claimed':
                return 'Claimed'

    def get_signature(self, current_timestamp: int) -> str:
        msg = f'By signing this message, I confirm ownership of this wallet, authorize the action to sign up for the Odyssey Community IP NFT, and that I have read and agree to the Privacy Policy (https://www.story.foundation/privacy-policy).\n\nThis signature does not authorize any other transactions or permissions.\n\nnonce: nDDNNO1U0DNbbahM6Z9n-{current_timestamp}.xa0Jap'
        signed_message = self.web3.eth.account.sign_message(
            encode_defunct(text=msg), private_key=self.private_key
        )
        signature = signed_message.signature.hex()
        return signature

    @retry(retries=RETRIES, delay=PAUSE_BETWEEN_RETRIES, backoff=1.5)
    async def claim_badge(self) -> Optional[bool]:
        eligible = await self.check_if_eligible()
        if not eligible:
            logger.error(f'[{self.wallet_address}] | Not eligible to claim.')
            return

        if eligible == 'Claimed':
            logger.success(f'[{self.wallet_address}] | Already claimed.')
            return True

        current_timestamp = int(time())
        signature = self.get_signature(current_timestamp)

        json_data = {
            'wallet': self.wallet_address,
            'signature': "0x" + signature,
            'message': f'By signing this message, I confirm ownership of this wallet, authorize the action to sign up for the Odyssey Community IP NFT, and that I have read and agree to the Privacy Policy (https://www.story.foundation/privacy-policy).\n\nThis signature does not authorize any other transactions or permissions.\n\nnonce: nDDNNO1U0DNbbahM6Z9n-{current_timestamp}.xa0Jap',
            'aux': '',
        }

        response_json, status = await self.make_request(
            method="POST",
            url='https://cm-mint.odyssey.storyapis.com/api/claim',
            headers=self.headers,
            json=json_data
        )

        if response_json['result'] == 'ok':
            logger.success(f'[{self.wallet_address}] | Successfully claimed badge')
            return True
