// lyriceng.asm — resident lyric-sprite engine for the Björk koala demo.
// Loaded once at $0c00 via mkpef --music (stays resident all 23 parts).
// Sprite shapes precomputed on host (lyric_spr.bin @ $2a00); engine only
// copies the current line's 8x24 bytes into the live VIC bank's sprite block
// on a line change. White hires sprites, 8-sprite 48-char row, bottom of screen.
//
// Entry jump table (called from part code / patched call_play):
//   $0c00 lyric_play   — every frame: SID play + advance + blit-on-change
//   $0c03 init_lyric   — part0 only: clear blocks, zero clock
//   $0c06 show_line    — force current line into BOTH banks (per-part setup)
//   $0c09 setup_sprites— set sprite regs + pointers ($0f: 0=bank1,1=bank2)

.const SPR   = $2a00          // 28 lines x 192 bytes
.const ONSET = $3f00          // 28 x 2 bytes (LE PAL frame stamp)
.const NLINES = 28
.const SID_PLAY = $1003
.const B1 = $4800             // bank1 sprite block (ptr $20)
.const B2 = $8800             // bank2 sprite block

.const FRAME = $05            // 16-bit frame counter ($05/$06)
.const CURSOR = $07           // current line index
.const LASTLINE = $08         // last blitted line ($ff = none)
.const SRC = $09              // $09/$0a
.const DST1 = $0b             // $0b/$0c
.const DST2 = $0d             // $0d/$0e
.const BANKF = $0f            // bank flag for setup_sprites

* = $0c00 "lyriceng"
        jmp lyric_play
        jmp init_lyric
        jmp show_line
        jmp setup_sprites

lyric_play:
        jsr SID_PLAY
        inc FRAME
        bne adv
        inc FRAME+1
adv:
        ldx CURSOR
        cpx #NLINES-1
        bcs adv_done
        inx
        txa
        asl
        tay                    // y = (cursor+1)*2
        lda FRAME+1
        cmp ONSET+1,y
        bcc adv_done
        bne adv_inc
        lda FRAME
        cmp ONSET,y
        bcc adv_done
adv_inc:
        inc CURSOR
        jmp adv
adv_done:
        lda CURSOR
        cmp LASTLINE
        beq lp_done
        sta LASTLINE
        jsr show_line
lp_done:
        rts

init_lyric:
        ldx #0
        lda #0
ic:
        sta B1,x
        sta B1+$100,x
        sta B2,x
        sta B2+$100,x
        inx
        bne ic
        lda #0
        sta FRAME
        sta FRAME+1
        sta CURSOR
        lda #$ff
        sta LASTLINE
        rts

// copy line CURSOR's shapes (8 sprites x 24 bytes) into both bank blocks,
// at block offset 21 (sprite rows 7-14).
show_line:
        lda #<SPR
        sta SRC
        lda #>SPR
        sta SRC+1
        ldx CURSOR
        beq sl_go
sl_mul:
        clc
        lda SRC
        adc #192
        sta SRC
        bcc sl_m1
        inc SRC+1
sl_m1:
        dex
        bne sl_mul
sl_go:
        lda #<(B1+21)
        sta DST1
        lda #>(B1+21)
        sta DST1+1
        lda #<(B2+21)
        sta DST2
        lda #>(B2+21)
        sta DST2+1
        ldx #8
sl_spr:
        ldy #23
sl_cp:
        lda (SRC),y
        sta (DST1),y
        sta (DST2),y
        dey
        bpl sl_cp
        clc
        lda SRC
        adc #24
        sta SRC
        bcc sl_s1
        inc SRC+1
sl_s1:
        clc
        lda DST1
        adc #64
        sta DST1
        bcc sl_s2
        inc DST1+1
sl_s2:
        clc
        lda DST2
        adc #64
        sta DST2
        bcc sl_s3
        inc DST2+1
sl_s3:
        dex
        bne sl_spr
        rts

setup_sprites:
        lda #$ff
        sta $d015              // enable all 8
        lda #0
        sta $d01c              // hires
        sta $d01b              // in front of bitmap
        sta $d017              // no Y expand
        sta $d01d              // no X expand
        sta $d010              // X MSB all 0 (X<256)
        ldx #7
        lda #1                 // white
ss_col:
        sta $d027,x
        dex
        bpl ss_col
        ldx #7
ss_xy:
        txa
        asl
        tay
        lda sprx,x
        sta $d000,y            // X
        lda #210
        sta $d001,y            // Y (bottom)
        dex
        bpl ss_xy
        lda BANKF
        bne ss_b2
        ldx #7
ss_p1:
        txa
        clc
        adc #$20
        sta $43f8,x            // bank1 sprite pointers
        dex
        bpl ss_p1
        rts
ss_b2:
        ldx #7
ss_p2:
        txa
        clc
        adc #$20
        sta $83f8,x            // bank2 sprite pointers
        dex
        bpl ss_p2
        rts

sprx:   .byte 84,108,132,156,180,204,228,252
