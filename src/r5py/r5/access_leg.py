#!/usr/bin/env python3


"""Represent one leg of a trip, specifically access to a public transport stop."""


from .transfer_leg import TransferLeg


__all__ = ["AccessLeg"]


class AccessLeg(TransferLeg):
    """Represent one leg of a trip, specifically access to a public transport stop."""
