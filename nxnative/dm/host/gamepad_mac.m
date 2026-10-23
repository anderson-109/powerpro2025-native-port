// One physical 1P controller through macOS GameController. User-selected Mac
// mapping: east=A (confirm), south=B (back), north=X, west=Y.
#import <Cocoa/Cocoa.h>
#import <GameController/GameController.h>
#include "dm_input.h"
#include "pad_axis.h"
#include <stdio.h>
#include <stdlib.h>
static GCController *g_mac_pad;
static float g_pad_deadzone;
static void mac_pad_publish(void) {
    GCExtendedGamepad *g = g_mac_pad.extendedGamepad;
    if (!g || !NSApp.active) { dm_pad_set(0, 0, 0, 0, 0); return; }
    uint64_t bits = 0;
#define K(button, bit) if ((button).isPressed) bits |= (bit)
    K(g.buttonB, DM_BTN_A); K(g.buttonA, DM_BTN_B);
    K(g.buttonY, DM_BTN_X); K(g.buttonX, DM_BTN_Y);
    K(g.leftShoulder, DM_BTN_L); K(g.rightShoulder, DM_BTN_R);
    K(g.leftTrigger, DM_BTN_ZL); K(g.rightTrigger, DM_BTN_ZR);
    K(g.buttonMenu, DM_BTN_PLUS); K(g.buttonOptions, DM_BTN_MINUS);
    K(g.leftThumbstickButton, DM_BTN_LS); K(g.rightThumbstickButton, DM_BTN_RS);
    K(g.dpad.left, DM_BTN_LEFT); K(g.dpad.up, DM_BTN_UP);
    K(g.dpad.right, DM_BTN_RIGHT); K(g.dpad.down, DM_BTN_DOWN);
#undef K
    dm_pad_set(bits, dm_pad_axis(g.leftThumbstick.xAxis.value, g_pad_deadzone),
               dm_pad_axis(g.leftThumbstick.yAxis.value, g_pad_deadzone),
               dm_pad_axis(g.rightThumbstick.xAxis.value, g_pad_deadzone),
               dm_pad_axis(g.rightThumbstick.yAxis.value, g_pad_deadzone));
}
static void mac_pad_refresh(void) {
    NSArray<GCController *> *pads = GCController.controllers;
    if (g_mac_pad && ![pads containsObject:g_mac_pad]) {
        g_mac_pad.extendedGamepad.valueChangedHandler = nil; g_mac_pad = nil;
        dm_pad_set(0, 0, 0, 0, 0);
        fprintf(stderr, "[dm] Mac controller disconnected: input released\n");
    }
    if (!g_mac_pad) for (GCController *c in pads) if (c.extendedGamepad) {
        g_mac_pad = c;
        // Serialize callbacks with connection/focus changes on the AppKit queue.
        c.handlerQueue = dispatch_get_main_queue();
        c.extendedGamepad.valueChangedHandler = ^(GCExtendedGamepad *g, GCControllerElement *element) {
            (void)element; if (g == g_mac_pad.extendedGamepad) mac_pad_publish();
        };
        fprintf(stderr, "[dm] Mac controller connected: %s (%s), east=confirm/south=back, front-end deadzone %.3f\n",
                c.vendorName.UTF8String ?: "unknown", c.productCategory.UTF8String ?: "unknown", g_pad_deadzone);
        break;
    }
    mac_pad_publish();
}
void mac_gamepad_start(void) {
    static BOOL started; if (started) return; started = YES;
    // Zero preserves GameController's calibrated values. An explicit optional
    // front-end deadzone is independent of Horizon's center-clamp detail flag.
    const char *e = getenv("DM_PAD_DEADZONE");
    if (e) { char *end; float v = strtof(e, &end);
        if (*e && !*end && isfinite(v) && v >= 0 && v < 0.5f) g_pad_deadzone = v;
        else fprintf(stderr, "[dm] [RED] invalid DM_PAD_DEADZONE: expected 0 <= value < 0.5; keeping 0\n");
    }
    NSNotificationCenter *nc = NSNotificationCenter.defaultCenter;
    for (NSNotificationName name in @[GCControllerDidConnectNotification, GCControllerDidDisconnectNotification,
                                      NSApplicationDidBecomeActiveNotification, NSApplicationDidResignActiveNotification])
        [nc addObserverForName:name object:nil queue:NSOperationQueue.mainQueue usingBlock:^(NSNotification *n) {
            if ([n.name isEqual:NSApplicationDidResignActiveNotification]) dm_pad_set(0, 0, 0, 0, 0);
            else mac_pad_refresh();
        }];
    mac_pad_refresh();
    fprintf(stderr, "[dm] Mac GameController monitoring active; extended controllers connected: %lu\n",
            (unsigned long)[GCController.controllers filteredArrayUsingPredicate:[NSPredicate predicateWithBlock:^BOOL(GCController *c, NSDictionary *bindings) { (void)bindings; return c.extendedGamepad != nil; }]].count);
}
