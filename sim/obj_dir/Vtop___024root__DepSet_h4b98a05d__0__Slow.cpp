// Verilated -*- C++ -*-
// DESCRIPTION: Verilator output: Design implementation internals
// See Vtop.h for the primary calling header

#include "Vtop__pch.h"
#include "Vtop__Syms.h"
#include "Vtop___024root.h"

VL_ATTR_COLD void Vtop___024root___configure_coverage(Vtop___024root* vlSelf, bool first) {
    (void)vlSelf;  // Prevent unused variable warning
    Vtop__Syms* const __restrict vlSymsp VL_ATTR_UNUSED = vlSelf->vlSymsp;
    VL_DEBUG_IF(VL_DBG_MSGF("+    Vtop___024root___configure_coverage\n"); );
    auto& vlSelfRef = std::ref(*vlSelf).get();
    // Body
    (void)first;  // Prevent unused variable warning
    vlSelf->__vlCoverInsert(&(vlSymsp->__Vcoverage[0]), first, "top.sv", 26, 18, ".top", "v_line/top", "if", "26-27");
    vlSelf->__vlCoverInsert(&(vlSymsp->__Vcoverage[1]), first, "top.sv", 26, 19, ".top", "v_line/top", "else", "28-29");
    vlSelf->__vlCoverInsert(&(vlSymsp->__Vcoverage[2]), first, "top.sv", 24, 18, ".top", "v_line/top", "elsif", "24-25");
    vlSelf->__vlCoverInsert(&(vlSymsp->__Vcoverage[3]), first, "top.sv", 22, 18, ".top", "v_line/top", "elsif", "22-23");
    vlSelf->__vlCoverInsert(&(vlSymsp->__Vcoverage[4]), first, "top.sv", 20, 18, ".top", "v_line/top", "elsif", "20-21");
    vlSelf->__vlCoverInsert(&(vlSymsp->__Vcoverage[5]), first, "top.sv", 18, 18, ".top", "v_line/top", "elsif", "18-19");
    vlSelf->__vlCoverInsert(&(vlSymsp->__Vcoverage[6]), first, "top.sv", 16, 18, ".top", "v_line/top", "elsif", "16-17");
    vlSelf->__vlCoverInsert(&(vlSymsp->__Vcoverage[7]), first, "top.sv", 14, 9, ".top", "v_line/top", "elsif", "14-15");
    vlSelf->__vlCoverInsert(&(vlSymsp->__Vcoverage[8]), first, "top.sv", 11, 5, ".top", "v_branch/top", "if", "11-12");
    vlSelf->__vlCoverInsert(&(vlSymsp->__Vcoverage[9]), first, "top.sv", 11, 6, ".top", "v_branch/top", "else", "13");
    vlSelf->__vlCoverInsert(&(vlSymsp->__Vcoverage[10]), first, "top.sv", 10, 1, ".top", "v_line/top", "block", "10");
}
