#!/usr/bin/env python3


"""Represent one leg of a trip, specifically egress from a public transport stop."""


from .transfer_leg import TransferLeg


__all__ = ["EgressLeg"]


class EgressLeg(TransferLeg):
    """Represent one leg of a trip, specifically egress from a public transport stop."""
