0000000000001220 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl>:
    1220:	mov    (%rdi),%rcx
    1223:	mov    0x8(%rdi),%rdx
    1227:	sub    %rcx,%rdx
    122a:	je     124d <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x2d>
    122c:	sar    $0x2,%rdx
    1230:	cmp    $0x1,%rdx
    1234:	mov    %rdx,%r8
    1237:	adc    $0x0,%r8
    123b:	mov    %r8d,%eax
    123e:	and    $0x7,%eax
    1241:	cmp    $0x8,%rdx
    1245:	jae    1253 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x33>
    1247:	xor    %edi,%edi
    1249:	xor    %edx,%edx
    124b:	jmp    12a8 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x88>
    124d:	xor    %edx,%edx
    124f:	mov    %rdx,(%rsi)
    1252:	ret
    1253:	and    $0xfffffffffffffff8,%r8
    1257:	xor    %edi,%edi
    1259:	xor    %edx,%edx
    125b:	nopl   0x0(%rax,%rax,1)
    1260:	movslq (%rcx,%rdi,4),%r9
    1264:	add    %rdx,%r9
    1267:	movslq 0x4(%rcx,%rdi,4),%rdx
    126c:	movslq 0x8(%rcx,%rdi,4),%r10
    1271:	add    %rdx,%r10
    1274:	add    %r9,%r10
    1277:	movslq 0xc(%rcx,%rdi,4),%rdx
    127c:	movslq 0x10(%rcx,%rdi,4),%r9
    1281:	add    %rdx,%r9
    1284:	movslq 0x14(%rcx,%rdi,4),%r11
    1289:	add    %r9,%r11
    128c:	add    %r10,%r11
    128f:	movslq 0x18(%rcx,%rdi,4),%r9
    1294:	movslq 0x1c(%rcx,%rdi,4),%rdx
    1299:	add    %r9,%rdx
    129c:	add    %r11,%rdx
    129f:	add    $0x8,%rdi
    12a3:	cmp    %rdi,%r8
    12a6:	jne    1260 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0x40>
    12a8:	test   %rax,%rax
    12ab:	je     12cf <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0xaf>
    12ad:	lea    (%rcx,%rdi,4),%rcx
    12b1:	xor    %edi,%edi
    12b3:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12c0:	movslq (%rcx,%rdi,4),%r8
    12c4:	add    %r8,%rdx
    12c7:	inc    %rdi
    12ca:	cmp    %rdi,%rax
    12cd:	jne    12c0 <_Z17kern_t01_sum_sizeRKNSt3__16vectorIiNS_9allocatorIiEEEEPl+0xa0>
    12cf:	mov    %rdx,(%rsi)
    12d2:	ret
    12d3:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
