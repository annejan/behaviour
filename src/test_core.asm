// test_core.asm — prove SID music + one koala in MCM bitmap.
// Standalone PRG (BASIC stub), not yet Spindle. VIC bank 1 ($4000-$7FFF):
//   screen RAM $4000, bitmap $6000-$7F3F, colour copied to $D800 at boot.
// Music (camping-sid PSID) sits at $1000-$296D, played 50Hz from raster IRQ.

.var music = LoadSid("human_behaviour.sid")
.var koala = LoadBinary("koala/img01.kla", BF_KOALA)

.const SCREEN = $4000          // VIC bank1 base, VM=0
.const BITMAP = $6000          // bank1 + $2000, CB bit3
.const COLDAT = $5000          // colour nibbles staged here, copied to $d800
.const framecnt = $02          // zp frame counter (read in VICE)

// ---- BASIC stub: SYS 2061 ----
* = $0801
.byte $0b,$08,$0a,$00,$9e,$32,$30,$36,$31,$00,$00,$00

* = $080d "entry"
        sei
        lda #$35
        sta $01                // RAM under KERNAL/BASIC (I/O still in)
        jsr setup_gfx
        lda #music.startSong-1
        jsr music.init
        lda #<irq
        sta $fffe
        lda #>irq
        sta $ffff
        lda #$7f
        sta $dc0d
        sta $dd0d              // disable CIA irq
        lda $dc0d
        lda $dd0d
        lda #$01
        sta $d01a             // enable raster irq
        lda #$f8
        sta $d012             // trigger in lower border
        lda #$3b
        sta $d011             // BMM+DEN+25row+ysc3, raster MSB=0
        lda $d019
        sta $d019
        cli
loop:   jmp loop

setup_gfx:
        lda $dd00
        and #$fc
        ora #$02
        sta $dd00            // VIC bank 1 ($4000-$7FFF)
        lda #$08
        sta $d018            // VM=$4000, bitmap=$6000
        lda #$3b
        sta $d011            // BMM=1 DEN=1 25row ysc=3
        lda #$18
        sta $d016            // MCM=1 40col
        lda #koala.getBackgroundColor()
        sta $d021
        lda #0
        sta $d020
        ldx #0
copycol:
        lda COLDAT,x
        sta $d800,x
        lda COLDAT+$100,x
        sta $d900,x
        lda COLDAT+$200,x
        sta $da00,x
        lda COLDAT+$2e8,x
        sta $dae8,x
        inx
        bne copycol
        rts

irq:
        pha
        txa
        pha
        tya
        pha
        inc framecnt
        jsr music.play
        lda $d019
        sta $d019
        pla
        tay
        pla
        tax
        pla
        rti

// ---- data ----
* = music.location "music"
        .fill music.size, music.getData(i)

* = SCREEN "screen"
        .fill 1000, koala.getScreenRam(i)

* = COLDAT "coldata"
        .fill 1000, koala.getColorRam(i)

* = BITMAP "bitmap"
        .fill 8000, koala.getBitmap(i)
