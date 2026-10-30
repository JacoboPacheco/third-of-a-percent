0000000000001220 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl>:
    1220:	test   %rsi,%rsi
    1223:	je     123a <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x1a>
    1225:	mov    (%rdi),%rcx
    1228:	mov    %esi,%eax
    122a:	and    $0x7,%eax
    122d:	cmp    $0x8,%rsi
    1231:	jae    1240 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x20>
    1233:	xor    %r8d,%r8d
    1236:	xor    %edi,%edi
    1238:	jmp    1298 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x78>
    123a:	xor    %edi,%edi
    123c:	mov    %rdi,(%rdx)
    123f:	ret
    1240:	and    $0xfffffffffffffff8,%rsi
    1244:	xor    %r8d,%r8d
    1247:	xor    %edi,%edi
    1249:	nopl   0x0(%rax)
    1250:	movslq (%rcx,%r8,4),%r9
    1254:	add    %rdi,%r9
    1257:	movslq 0x4(%rcx,%r8,4),%rdi
    125c:	movslq 0x8(%rcx,%r8,4),%r10
    1261:	add    %rdi,%r10
    1264:	add    %r9,%r10
    1267:	movslq 0xc(%rcx,%r8,4),%rdi
    126c:	movslq 0x10(%rcx,%r8,4),%r9
    1271:	add    %rdi,%r9
    1274:	movslq 0x14(%rcx,%r8,4),%r11
    1279:	add    %r9,%r11
    127c:	add    %r10,%r11
    127f:	movslq 0x18(%rcx,%r8,4),%r9
    1284:	movslq 0x1c(%rcx,%r8,4),%rdi
    1289:	add    %r9,%rdi
    128c:	add    %r11,%rdi
    128f:	add    $0x8,%r8
    1293:	cmp    %r8,%rsi
    1296:	jne    1250 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x30>
    1298:	test   %rax,%rax
    129b:	je     12bf <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x9f>
    129d:	lea    (%rcx,%r8,4),%rcx
    12a1:	xor    %esi,%esi
    12a3:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b0:	movslq (%rcx,%rsi,4),%r8
    12b4:	add    %r8,%rdi
    12b7:	inc    %rsi
    12ba:	cmp    %rsi,%rax
    12bd:	jne    12b0 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x90>
    12bf:	mov    %rdi,(%rdx)
    12c2:	ret
    12c3:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
