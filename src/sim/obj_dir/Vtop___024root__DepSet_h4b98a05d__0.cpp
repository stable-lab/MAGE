// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "Vtop__pch.h"
#include "Vtop__Syms.h"
#include "Vtop___024root.h"

#ifdef VL_DEBUG
VL_ATTR_COLD void Vtop___024root___dump_triggers__act(Vtop___024root* vlSelf);
#endif  // VL_DEBUG

void Vtop___024root___eval_triggers__act(Vtop___024root* vlSelf) {
    (void)vlSelf;  // Prevent unused variable warning
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___eval_triggers__act\n"); );
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    vlSelfRef.__VactTriggered.set(0U, ((IData)(vlSelfRef.clk) 
                                       & (~ (IData)(vlSelfRef.__Vtrigprevexpr___TOP__clk__0))));
    vlSelfRef.__Vtrigprevexpr___TOP__clk__0 = vlSelfRef.clk;
#ifdef VL_DEBUG
    if (VL_UNLIKELY(vlSymsp->_vm_contextp__->debug())) {
        Vtop___024root___dump_triggers__act(vlSelf);
    }
#endif
}

VL_INLINE_OPT void Vtop___024root___nba_sequent__TOP__0(Vtop___024root* vlSelf) {
    (void)vlSelf;  // Prevent unused variable warning
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___nba_sequent__TOP__0\n"); );
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    if (vlSelfRef.rst) {
        ++(vlSymsp->__Vcoverage[8]);
        vlSelfRef.output_data = 0U;
    } else {
        if ((0xffU == (IData)(vlSelfRef.input_data))) {
            ++(vlSymsp->__Vcoverage[7]);
            vlSelfRef.output_data = (0xffU & VL_SHIFTL_III(8,8,32, (IData)(vlSelfRef.input_data), 1U));
        } else if ((0xf8U < (IData)(vlSelfRef.input_data))) {
            ++(vlSymsp->__Vcoverage[6]);
            vlSelfRef.output_data = (0xffU & ((IData)(0xfU) 
                                              + (IData)(vlSelfRef.input_data)));
        } else if ((0xe0U < (IData)(vlSelfRef.input_data))) {
            ++(vlSymsp->__Vcoverage[5]);
            vlSelfRef.output_data = (0xffU & ((IData)(vlSelfRef.input_data) 
                                              - (IData)(0x10U)));
        } else if ((0xa0U < (IData)(vlSelfRef.input_data))) {
            ++(vlSymsp->__Vcoverage[4]);
            vlSelfRef.output_data = (0xffU & ((IData)(vlSelfRef.input_data) 
                                              - (IData)(0x11U)));
        } else if ((0x80U < (IData)(vlSelfRef.input_data))) {
            ++(vlSymsp->__Vcoverage[3]);
            vlSelfRef.output_data = (0xffU & ((IData)(vlSelfRef.input_data) 
                                              - (IData)(0x22U)));
        } else if ((0x40U < (IData)(vlSelfRef.input_data))) {
            ++(vlSymsp->__Vcoverage[2]);
            vlSelfRef.output_data = (0xffU & ((IData)(vlSelfRef.input_data) 
                                              - (IData)(0x33U)));
        } else if ((0U < (IData)(vlSelfRef.input_data))) {
            ++(vlSymsp->__Vcoverage[0]);
            vlSelfRef.output_data = (0xffU & ((IData)(vlSelfRef.input_data) 
                                              - (IData)(0x44U)));
        } else {
            ++(vlSymsp->__Vcoverage[1]);
            vlSelfRef.output_data = vlSelfRef.input_data;
        }
        ++(vlSymsp->__Vcoverage[9]);
    }
    ++(vlSymsp->__Vcoverage[10]);
}
