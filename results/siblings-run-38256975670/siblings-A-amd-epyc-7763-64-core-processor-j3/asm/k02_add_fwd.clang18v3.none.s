0000000000001220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%rcx
    1227:	sub    %rax,%rcx
    122a:	je     13c3 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x1a3>
    1230:	sar    $0x2,%rcx
    1234:	mov    (%rdx),%rdx
    1237:	mov    (%rdi),%rsi
    123a:	cmp    $0x1,%rcx
    123e:	mov    %rcx,%rdi
    1241:	adc    $0x0,%rdi
    1245:	cmp    $0x20,%rcx
    1249:	jae    1323 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x103>
    124f:	xor    %r8d,%r8d
    1252:	mov    %rdi,%r10
    1255:	mov    %r8,%r9
    1258:	and    $0x7,%r10
    125c:	je     1284 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x64>
    125e:	mov    %r8,%r9
    1261:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1270:	mov    (%rdx,%r9,4),%r11d
    1274:	add    (%rax,%r9,4),%r11d
    1278:	mov    %r11d,(%rsi,%r9,4)
    127c:	inc    %r9
    127f:	dec    %r10
    1282:	jne    1270 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x50>
    1284:	sub    %rdi,%r8
    1287:	cmp    $0xfffffffffffffff8,%r8
    128b:	ja     13c3 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x1a3>
    1291:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12a0:	mov    (%rdx,%r9,4),%edi
    12a4:	add    (%rax,%r9,4),%edi
    12a8:	mov    %edi,(%rsi,%r9,4)
    12ac:	mov    0x4(%rdx,%r9,4),%edi
    12b1:	add    0x4(%rax,%r9,4),%edi
    12b6:	mov    %edi,0x4(%rsi,%r9,4)
    12bb:	mov    0x8(%rdx,%r9,4),%edi
    12c0:	add    0x8(%rax,%r9,4),%edi
    12c5:	mov    %edi,0x8(%rsi,%r9,4)
    12ca:	mov    0xc(%rdx,%r9,4),%edi
    12cf:	add    0xc(%rax,%r9,4),%edi
    12d4:	mov    %edi,0xc(%rsi,%r9,4)
    12d9:	mov    0x10(%rdx,%r9,4),%edi
    12de:	add    0x10(%rax,%r9,4),%edi
    12e3:	mov    %edi,0x10(%rsi,%r9,4)
    12e8:	mov    0x14(%rdx,%r9,4),%edi
    12ed:	add    0x14(%rax,%r9,4),%edi
    12f2:	mov    %edi,0x14(%rsi,%r9,4)
    12f7:	mov    0x18(%rdx,%r9,4),%edi
    12fc:	add    0x18(%rax,%r9,4),%edi
    1301:	mov    %edi,0x18(%rsi,%r9,4)
    1306:	mov    0x1c(%rdx,%r9,4),%edi
    130b:	add    0x1c(%rax,%r9,4),%edi
    1310:	mov    %edi,0x1c(%rsi,%r9,4)
    1315:	add    $0x8,%r9
    1319:	cmp    %r9,%rcx
    131c:	jne    12a0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x80>
    131e:	jmp    13c3 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x1a3>
    1323:	mov    %rsi,%r9
    1326:	sub    %rax,%r9
    1329:	xor    %r8d,%r8d
    132c:	cmp    $0x80,%r9
    1333:	jb     1252 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    1339:	mov    %rsi,%r9
    133c:	sub    %rdx,%r9
    133f:	cmp    $0x80,%r9
    1346:	jb     1252 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    134c:	mov    %rdi,%r8
    134f:	and    $0xffffffffffffffe0,%r8
    1353:	xor    %r9d,%r9d
    1356:	cs nopw 0x0(%rax,%rax,1)
    1360:	vmovdqu (%rdx,%r9,4),%ymm0
    1366:	vmovdqu 0x20(%rdx,%r9,4),%ymm1
    136d:	vmovdqu 0x40(%rdx,%r9,4),%ymm2
    1374:	vmovdqu 0x60(%rdx,%r9,4),%ymm3
    137b:	vpaddd (%rax,%r9,4),%ymm0,%ymm0
    1381:	vpaddd 0x20(%rax,%r9,4),%ymm1,%ymm1
    1388:	vpaddd 0x40(%rax,%r9,4),%ymm2,%ymm2
    138f:	vpaddd 0x60(%rax,%r9,4),%ymm3,%ymm3
    1396:	vmovdqu %ymm0,(%rsi,%r9,4)
    139c:	vmovdqu %ymm1,0x20(%rsi,%r9,4)
    13a3:	vmovdqu %ymm2,0x40(%rsi,%r9,4)
    13aa:	vmovdqu %ymm3,0x60(%rsi,%r9,4)
    13b1:	add    $0x20,%r9
    13b5:	cmp    %r9,%r8
    13b8:	jne    1360 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x140>
    13ba:	cmp    %r8,%rdi
    13bd:	jne    1252 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x32>
    13c3:	vzeroupper
    13c6:	ret
    13c7:	nopw   0x0(%rax,%rax,1)
