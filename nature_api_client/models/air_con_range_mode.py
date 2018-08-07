# coding: utf-8

"""
    Nature API

    Read/Write Nature Remo  # noqa: E501

    OpenAPI spec version: 1.0.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six

from nature_api_client.models.air_direction import AirDirection  # noqa: F401,E501
from nature_api_client.models.air_volume import AirVolume  # noqa: F401,E501
from nature_api_client.models.temperature import Temperature  # noqa: F401,E501


class AirConRangeMode(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'temp': 'list[Temperature]',
        'vol': 'list[AirVolume]',
        'dir': 'list[AirDirection]'
    }

    attribute_map = {
        'temp': 'temp',
        'vol': 'vol',
        'dir': 'dir'
    }

    def __init__(self, temp=None, vol=None, dir=None):  # noqa: E501
        """AirConRangeMode - a model defined in Swagger"""  # noqa: E501

        self._temp = None
        self._vol = None
        self._dir = None
        self.discriminator = None

        if temp is not None:
            self.temp = temp
        if vol is not None:
            self.vol = vol
        if dir is not None:
            self.dir = dir

    @property
    def temp(self):
        """Gets the temp of this AirConRangeMode.  # noqa: E501


        :return: The temp of this AirConRangeMode.  # noqa: E501
        :rtype: list[Temperature]
        """
        return self._temp

    @temp.setter
    def temp(self, temp):
        """Sets the temp of this AirConRangeMode.


        :param temp: The temp of this AirConRangeMode.  # noqa: E501
        :type: list[Temperature]
        """

        self._temp = temp

    @property
    def vol(self):
        """Gets the vol of this AirConRangeMode.  # noqa: E501


        :return: The vol of this AirConRangeMode.  # noqa: E501
        :rtype: list[AirVolume]
        """
        return self._vol

    @vol.setter
    def vol(self, vol):
        """Sets the vol of this AirConRangeMode.


        :param vol: The vol of this AirConRangeMode.  # noqa: E501
        :type: list[AirVolume]
        """

        self._vol = vol

    @property
    def dir(self):
        """Gets the dir of this AirConRangeMode.  # noqa: E501


        :return: The dir of this AirConRangeMode.  # noqa: E501
        :rtype: list[AirDirection]
        """
        return self._dir

    @dir.setter
    def dir(self, dir):
        """Sets the dir of this AirConRangeMode.


        :param dir: The dir of this AirConRangeMode.  # noqa: E501
        :type: list[AirDirection]
        """

        self._dir = dir

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, AirConRangeMode):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
