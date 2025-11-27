import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from preprocessor import util


def preprocess_post(body=None):  # noqa: E501
    """preprocess_post

    Preprocesses an ePI. Receives an ePI and returns it preprocessed. # noqa: E501

    :param body: ePI to preprocess.
    :type body: 

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    body = body
    return 'do some magic!'
