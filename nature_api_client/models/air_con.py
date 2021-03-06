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

from nature_api_client.models.air_con_range import AirConRange  # noqa: F401,E501


class AirCon(object):
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
        'range': 'AirConRange',
        'temp_unit': 'str'
    }

    attribute_map = {
        'range': 'range',
        'temp_unit': 'tempUnit'
    }

    def __init__(self, range=None, temp_unit=None):  # noqa: E501
        """AirCon - a model defined in Swagger"""  # noqa: E501

        self._range = None
        self._temp_unit = None
        self.discriminator = None

        if range is not None:
            self.range = range
        if temp_unit is not None:
            self.temp_unit = temp_unit

    @property
    def range(self):
        """Gets the range of this AirCon.  # noqa: E501


        :return: The range of this AirCon.  # noqa: E501
        :rtype: AirConRange
        """
        return self._range

    @range.setter
    def range(self, range):
        """Sets the range of this AirCon.


        :param range: The range of this AirCon.  # noqa: E501
        :type: AirConRange
        """

        self._range = range

    @property
    def temp_unit(self):
        """Gets the temp_unit of this AirCon.  # noqa: E501


        :return: The temp_unit of this AirCon.  # noqa: E501
        :rtype: str
        """
        return self._temp_unit

    @temp_unit.setter
    def temp_unit(self, temp_unit):
        """Sets the temp_unit of this AirCon.


        :param temp_unit: The temp_unit of this AirCon.  # noqa: E501
        :type: str
        """
        allowed_values = ["", "c", "f"]  # noqa: E501
        if temp_unit not in allowed_values:
            raise ValueError(
                "Invalid value for `temp_unit` ({0}), must be one of {1}"  # noqa: E501
                .format(temp_unit, allowed_values)
            )

        self._temp_unit = temp_unit

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
        if not isinstance(other, AirCon):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
