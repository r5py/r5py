#!/usr/bin/env python3


"""Represent one leg of a trip: transfers between public transport vehicles."""

from .direct_leg import DirectLeg

__all__ = ["TransferLeg"]


class TransferLeg(DirectLeg):
    """Represent one leg of a trip: transfers between public transport vehicles."""
