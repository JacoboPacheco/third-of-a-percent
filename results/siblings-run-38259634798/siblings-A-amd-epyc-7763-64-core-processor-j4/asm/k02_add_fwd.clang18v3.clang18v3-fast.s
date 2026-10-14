0000000000001220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1220:	mov    (%rsi),%r8
    1223:	mov    0x8(%rsi),%rax
    1227:	sub    %r8,%rax
    122a:	je     131e <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xfe>
    1230:	sar    $0x2,%rax
    1234:	mov    (%rdx),%rsi
    1237:	mov    0x8(%rdx),%rcx
    123b:	sub    %rsi,%rcx
    123e:	sar    $0x2,%rcx
    1242:	mov    (%rdi),%r9
    1245:	mov    0x8(%rdi),%rdx
    1249:	sub    %r9,%rdx
    124c:	sar    $0x2,%rdx
    1250:	cmp    $0x1,%rax
    1254:	adc    $0x0,%rax
    1258:	lea    -0x1(%rax),%r10
    125c:	cmp    %rdx,%r10
    125f:	cmovae %rdx,%r10
    1263:	cmp    %rcx,%r10
    1266:	cmovae %rcx,%r10
    126a:	cmp    $0xf,%r10
    126e:	ja     1274 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x54>
    1270:	xor    %edi,%edi
    1272:	jmp    12e0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc0>
    1274:	mov    %r9,%r11
    1277:	sub    %r8,%r11
    127a:	xor    %edi,%edi
    127c:	cmp    $0x40,%r11
    1280:	jb     12e0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc0>
    1282:	mov    %r9,%r11
    1285:	sub    %rsi,%r11
    1288:	cmp    $0x40,%r11
    128c:	jb     12e0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc0>
    128e:	inc    %r10
    1291:	mov    %r10d,%edi
    1294:	and    $0xf,%edi
    1297:	mov    $0x10,%r11d
    129d:	cmovne %rdi,%r11
    12a1:	mov    %r10,%rdi
    12a4:	sub    %r11,%rdi
    12a7:	xor    %r10d,%r10d
    12aa:	nopw   0x0(%rax,%rax,1)
    12b0:	vmovdqu (%rsi,%r10,4),%ymm0
    12b6:	vmovdqu 0x20(%rsi,%r10,4),%ymm1
    12bd:	vpaddd (%r8,%r10,4),%ymm0,%ymm0
    12c3:	vpaddd 0x20(%r8,%r10,4),%ymm1,%ymm1
    12ca:	vmovdqu %ymm0,(%r9,%r10,4)
    12d0:	vmovdqu %ymm1,0x20(%r9,%r10,4)
    12d7:	add    $0x10,%r10
    12db:	cmp    %r10,%rdi
    12de:	jne    12b0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x90>
    12e0:	sub    %rdi,%rdx
    12e3:	sub    %rdi,%rcx
    12e6:	sub    %rdi,%rax
    12e9:	lea    (%r8,%rdi,4),%r8
    12ed:	lea    (%rsi,%rdi,4),%rsi
    12f1:	lea    (%r9,%rdi,4),%rdi
    12f5:	xor    %r9d,%r9d
    12f8:	nopl   0x0(%rax,%rax,1)
    1300:	cmp    %r9,%rcx
    1303:	je     1322 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x102>
    1305:	cmp    %r9,%rdx
    1308:	je     1322 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x102>
    130a:	mov    (%rsi,%r9,4),%r10d
    130e:	add    (%r8,%r9,4),%r10d
    1312:	mov    %r10d,(%rdi,%r9,4)
    1316:	inc    %r9
    1319:	cmp    %r9,%rax
    131c:	jne    1300 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xe0>
    131e:	vzeroupper
    1321:	ret
    1322:	ud2
    1324:	data16 data16 cs nopw 0x0(%rax,%rax,1)
