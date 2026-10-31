// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title AnchorLog
/// @notice Append-only log de raices Merkle. Sin admin, sin upgrade, sin pausa.
///         Cada root solo puede anclarse una vez. Metadata minima.
contract AnchorLog {
    struct Anchor {
        bytes32 root;
        uint256 size;
        uint256 ts;
        address by;
    }

    Anchor[] private _anchors;
    mapping(bytes32 => uint256) private _seqOf; // root -> seq+1 (0 = no anclada)

    event Anchored(
        uint256 indexed seq,
        bytes32 indexed root,
        uint256 size,
        address indexed by,
        uint256 ts
    );

    error EmptyRoot();
    error AlreadyAnchored(bytes32 root);
    error SizeZero();

    function anchor(bytes32 root, uint256 size) external returns (uint256 seq) {
        if (root == bytes32(0)) revert EmptyRoot();
        if (size == 0) revert SizeZero();
        if (_seqOf[root] != 0) revert AlreadyAnchored(root);

        _anchors.push(Anchor({ root: root, size: size, ts: block.timestamp, by: msg.sender }));
        seq = _anchors.length - 1;
        _seqOf[root] = seq + 1;

        emit Anchored(seq, root, size, msg.sender, block.timestamp);
    }

    function count() external view returns (uint256) { return _anchors.length; }

    function get(uint256 seq) external view returns (Anchor memory) { return _anchors[seq]; }

    function seqOf(bytes32 root) external view returns (uint256) {
        uint256 v = _seqOf[root];
        return v == 0 ? type(uint256).max : v - 1;
    }

    function isAnchored(bytes32 root) external view returns (bool) { return _seqOf[root] != 0; }
}
